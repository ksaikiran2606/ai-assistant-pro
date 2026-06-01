"""MySQL connection helpers (SSL for Aiven / cloud hosts)."""

import logging
import os
import ssl
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def build_mysql_connect_args(
    database_url: str,
    ssl_ca_pem: str = "",
    ssl_ca_file: str = "",
    allow_insecure_ssl: bool = False,
) -> dict:
    """Build pymysql connect_args with optional SSL CA for cloud MySQL (e.g. Aiven)."""
    args: dict = {"charset": "utf8mb4"}
    ca_path: str | None = None

    pem = (ssl_ca_pem or "").strip().replace("\\n", "\n")
    if pem:
        fd, path = tempfile.mkstemp(suffix=".pem")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(pem)
        ca_path = path
    elif ssl_ca_file:
        file_path = Path(ssl_ca_file)
        if not file_path.is_absolute():
            backend_root = Path(__file__).resolve().parent.parent
            file_path = backend_root / ssl_ca_file
        if file_path.is_file():
            ca_path = str(file_path)

    if ca_path:
        args["ssl"] = {"ca": ca_path}
    elif "aivencloud.com" in database_url:
        if allow_insecure_ssl:
            # Dev fallback only — use ca.pem or MYSQL_SSL_CA in production
            logger.warning(
                "Aiven SSL: no CA cert found. Using insecure SSL for development. "
                "Download CA from Aiven → save as backend/certs/ca.pem"
            )
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            args["ssl"] = ctx
        else:
            raise RuntimeError(
                "Aiven MySQL requires SSL CA certificate. "
                "Download from Aiven → Connection info → CA certificate → "
                "save as backend/certs/ca.pem OR set MYSQL_SSL_CA env var."
            )

    return args
