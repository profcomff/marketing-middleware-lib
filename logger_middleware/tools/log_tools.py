import asyncio
import json

import httpx
from fastapi import Request

from logger_middleware.settings import get_settings
from logger_middleware.tools.get_user_id import get_user_id
from logger_middleware.tools.console_logger_tools import logger as log

settings = get_settings()


async def send_log(url, log_data):
    """Отправляем лог на внешний сервис асинхронно с ретраями."""
    async with httpx.AsyncClient() as client:
        for attempt, sleep_time in enumerate(settings.RETRY_DELAYS, start=1):
            try:
                response = await client.post(url=url, json=log_data)

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


async def log_request(
    url, service_id, request: Request, status_code: int, json_body: dict
):
    """Формирует лог и отправляет его в фоновую задачу."""
    additional_data = {
        "response_status_code": status_code,
        "auth_user_id": await get_user_id(request),
        "query": request.url.path + "?" + request.url.query,
        "request": json_body,
    }
    log_data = {
        "user_id": service_id,
        "action": request.method,
        "additional_data": json.dumps(additional_data),
        "path_from": "",
        "path_to": request.url.path,
    }
    asyncio.create_task(send_log(url, log_data))
