import os

import sentry_sdk
from dotenv import load_dotenv

from .app import create_app


def check_required_env(*names: str) -> None:
    missing_names = [name for name in names if not os.getenv(name)]
    if missing_names:
        names_list = ", ".join(missing_names)
        raise RuntimeError(f"Missing required env vars: {names_list}")


def init_sentry():
    sentry_dsn = os.environ.get("SENTRY_DSN", None)
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
        )


load_dotenv()
check_required_env("DATABASE_URL", "BASE_URL")
init_sentry()
app = create_app()
