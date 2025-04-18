import os

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from logger_middleware.settings import get_settings
from logger_middleware.tools.get_request_body import get_request_body
from logger_middleware.tools.log_tools import log_request


class LoggerMiddleware(BaseHTTPMiddleware):
    """Нужно прописать если локально env MARKETING_PORT, иначе APP_VERSION"""

    settings = get_settings()

    def __init__(self, app: FastAPI, service_id: int):
        """service_id для уникального id прилодения или сервиса на которого логируем запросы."""
        super().__init__(app)
        self.service_id = service_id
        self.__LOGGING_MARKETING_URL: str = self.settings.LOGGING_MARKETING_URLS.get(
            os.getenv("APP_VERSION", "dev"),
            self.settings.LOGGING_MARKETING_URLS["test"],
        )

    async def dispatch(self, request: Request, call_next):
        """Основной middleware, который логирует запрос и восстанавливает тело."""
        try:
            request, json_body = await get_request_body(request)
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            response = Response(content="Internal server error", status_code=500)

        await log_request(
            url=self.__LOGGING_MARKETING_URL,
            service_id=self.service_id,
            request=request,
            status_code=status_code,
            json_body=json_body,
        )

        return response
