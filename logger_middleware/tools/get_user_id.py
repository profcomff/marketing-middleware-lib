from auth_lib.fastapi import UnionAuth
from fastapi import Request

from logger_middleware.tools.console_logger_tools import logger as log


async def get_user_id(request: Request):
    """Получает user_id из UnionAuth."""
    user_id = "Not auth"
    try:
        auth = UnionAuth(auto_error=False)(request)
        if auth is not None:  # Если успешна авторизация и передан токен.
            user_id = auth.get("id")
    except Exception as e:
        user_id = -1
        log.error(f"USER_AUTH: {e}")

    return user_id
