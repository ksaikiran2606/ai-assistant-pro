/** Parse FastAPI / axios error responses into a user-friendly string. */
export function parseApiError(error, fallback = 'Something went wrong') {
  const detail = error?.response?.data?.detail;

  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = item.loc?.slice(-1)[0];
        const label = field === 'email' ? 'Email' : field === 'password' ? 'Password' : field;
        return `${label}: ${item.msg}`;
      })
      .join('. ');
  }

  return fallback;
}
