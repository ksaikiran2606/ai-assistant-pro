"""AI provider abstraction with OpenAI, Gemini, and Groq support."""

from typing import AsyncGenerator, List

from app.config import get_settings

GEMINI_FALLBACK_MODELS = ("gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash-latest")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class AIProviderError(Exception):
    """User-facing AI provider error."""


def friendly_ai_error(exc: Exception | str, provider: str = "AI") -> str:
    err = str(exc).lower()
    provider_key = provider.lower()

    if any(x in err for x in ("429", "quota", "rate limit", "resource_exhausted", "too many requests")):
        if provider_key == "gemini":
            return (
                "Gemini free quota exceeded. Wait a few minutes and try again, "
                "or create a new key at https://aistudio.google.com/apikey"
            )
        if provider_key == "openai":
            return "OpenAI rate limit or quota exceeded. Check billing at https://platform.openai.com/account/billing"
        if provider_key == "groq":
            return "Groq rate limit exceeded. Wait a moment or check usage at https://console.groq.com"
        return f"{provider} quota or rate limit exceeded. Check your API plan."

    if any(x in err for x in ("401", "403", "invalid api key", "permission denied", "api key not valid")):
        return f"Invalid {provider} API key. Update your key in backend/.env"

    if "404" in err or "not found" in err:
        return f"{provider} model not available. Check the model name in backend/.env"

    if "not configured" in err:
        return str(exc)

    return f"{provider} request failed. Verify your API key and provider settings in backend/.env"


class AIService:
    """Unified interface for AI chat completions with streaming."""

    async def stream_response(
        self, messages: List[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        provider = get_settings().ai_provider.lower()
        if provider == "gemini":
            async for chunk in self._stream_gemini(messages):
                yield chunk
        elif provider == "groq":
            async for chunk in self._stream_groq(messages):
                yield chunk
        else:
            async for chunk in self._stream_openai(messages):
                yield chunk

    async def _stream_openai_compatible(
        self,
        messages: List[dict[str, str]],
        *,
        api_key: str,
        model: str,
        provider_name: str,
        base_url: str | None = None,
    ) -> AsyncGenerator[str, None]:
        from openai import AsyncOpenAI

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = AsyncOpenAI(**client_kwargs)
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=4096,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def _stream_openai(
        self, messages: List[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        settings = get_settings()
        if not settings.openai_api_key or settings.openai_api_key.startswith("your-"):
            raise AIProviderError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in backend/.env "
                "or use AI_PROVIDER=groq for free testing."
            )
        try:
            async for chunk in self._stream_openai_compatible(
                messages,
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                provider_name="OpenAI",
            ):
                yield chunk
        except Exception as exc:
            raise AIProviderError(friendly_ai_error(exc, "OpenAI")) from exc

    async def _stream_groq(
        self, messages: List[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        settings = get_settings()
        if not settings.groq_api_key or settings.groq_api_key.startswith("your-"):
            raise AIProviderError(
                "Groq API key not configured. Get a free key at https://console.groq.com/keys "
                "and set GROQ_API_KEY in backend/.env"
            )
        try:
            async for chunk in self._stream_openai_compatible(
                messages,
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                provider_name="Groq",
                base_url=GROQ_BASE_URL,
            ):
                yield chunk
        except Exception as exc:
            raise AIProviderError(friendly_ai_error(exc, "Groq")) from exc

    def _build_gemini_chat(self, messages: List[dict[str, str]]):
        system_instruction = None
        history: list[dict] = []

        for msg in messages[:-1]:
            role, content = msg["role"], msg["content"]
            if role == "system":
                system_instruction = content
            elif role == "user":
                history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})

        last_user_message = messages[-1]["content"] if messages else ""
        return system_instruction, history, last_user_message

    async def _gemini_stream_model(
        self, model_name: str, messages: List[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        import google.generativeai as genai

        system_instruction, history, last_message = self._build_gemini_chat(messages)
        model = genai.GenerativeModel(
            model_name,
            system_instruction=system_instruction,
        )
        chat = model.start_chat(history=history)
        response = await chat.send_message_async(last_message, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def _stream_gemini(
        self, messages: List[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        import google.generativeai as genai

        settings = get_settings()
        if not settings.gemini_api_key or settings.gemini_api_key.startswith("your-"):
            raise AIProviderError("Gemini API key not configured in backend/.env")

        genai.configure(api_key=settings.gemini_api_key)

        models_to_try = [settings.gemini_model]
        for fallback in GEMINI_FALLBACK_MODELS:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error: Exception | None = None
        for model_name in models_to_try:
            try:
                async for chunk in self._gemini_stream_model(model_name, messages):
                    yield chunk
                return
            except Exception as exc:
                last_error = exc
                err = str(exc).lower()
                if any(x in err for x in ("429", "quota", "401", "403", "invalid", "permission")):
                    raise AIProviderError(friendly_ai_error(exc, "Gemini")) from exc
                if "404" in err or "not found" in err or "not supported" in err:
                    continue
                raise AIProviderError(friendly_ai_error(exc, "Gemini")) from exc

        raise AIProviderError(
            friendly_ai_error(last_error or "Gemini request failed", "Gemini")
        )


ai_service = AIService()
