import asyncio
import json
import os

import httpx
from auth_lib.fastapi import UnionAuth
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN

from .logger_tool import logger as log

RETRY_DELAYS = [2, 4, 8]  # Задержки перед повторными попытками


class LoggerMiddleware(BaseHTTPMiddleware):
    """Нужно прописать если локально env MARKETING_PORT, иначе APP_VERSION"""

    __LOGGING_MARKETING_URLS = {
        "dev": f"http://localhost:{os.getenv('MARKETING_PORT', 8000)}/v1/action",
        "test": "https://api.test.profcomff.com/marketing/v1/action",
        "prod": "https://api.profcomff.com/marketing/v1/action",
    }

    def __init__(self, app: FastAPI, service_id: int):
        """service_id для уникального id прилодения или сервиса на которого логируем запросы."""
        super().__init__(app)
        self.service_id = service_id
        self.__LOGGING_MARKETING_URL: str = self.__LOGGING_MARKETING_URLS.get(
            os.getenv("APP_VERSION", "dev"), self.__LOGGING_MARKETING_URLS["test"]
        )

    async def dispatch(self, request: Request, call_next):
        """Основной middleware, который логирует запрос и восстанавливает тело."""
        try:
            request, json_body = await self.get_request_body(request)
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            response = Response(content="Internal server error", status_code=500)

        await self.log_request(request, status_code, json_body)

        return response

    async def send_log(self, log_data):
        """Отправляем лог на внешний сервис асинхронно с ретраями."""
        async with httpx.AsyncClient() as client:
            for attempt, sleep_time in enumerate(RETRY_DELAYS, start=1):
                try:
                    response = await client.post(
                        self.__LOGGING_MARKETING_URL, json=log_data
                    )

                    if response.status_code not in {408, 409, 429, 500, 502, 503, 504}:
                        log.info(f"Ответ записи логов: {response.status_code}")
                        break  # Успешно

                except httpx.RequestError as e:
                    log.warning(f"Ошибка сети логов: {e}")

                except Exception as e:
                    log.warning(f"Неизвестная ошибка логов: {e}")

                await asyncio.sleep(sleep_time)

            else:
                log.warning("Не удалось отправить лог после нескольких попыток.")

    async def get_request_body(self, request: Request) -> tuple[Request, dict]:
        """Читает тело запроса и возвращает новый request и тело в виде JSON."""
        body = await request.body()
        json_body = json.loads(body) if body else {}

        async def new_stream():
            yield body

        return Request(request.scope, receive=new_stream()), json_body

    async def get_user_id(self, request: Request):
        """Получает user_id из UnionAuth."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            user_id = "Not auth"
        else:
            try:
                user_id = UnionAuth()(request).get("id")
            except HTTPException as e:
                if e.status_code == HTTP_403_FORBIDDEN:
                    log.warning(f"USER_AUTH: Not authenticated — {e.detail}")
                    return "Not auth"
            except Exception as e:
                user_id = -1
                log.error(f"USER_AUTH: {e}")

        return user_id

    async def log_request(self, request: Request, status_code: int, json_body: dict):
        """Формирует лог и отправляет его в фоновую задачу."""
        additional_data = {
            "response_status_code": status_code,
            "auth_user_id": await self.get_user_id(request),
            "query": request.url.path + "?" + request.url.query,
            "request": json_body,
        }
        log_data = {
            "user_id": self.service_id,
            "action": request.method,
            "additional_data": json.dumps(additional_data),
            "path_from": "",
            "path_to": request.url.path,
        }
        asyncio.create_task(self.send_log(log_data))
