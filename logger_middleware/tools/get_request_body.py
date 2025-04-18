import json

from fastapi import Request


async def get_request_body(request: Request) -> tuple[Request, dict]:
    """Читает тело запроса и возвращает новый request и тело в виде JSON."""
    body = await request.body()
    json_body = json.loads(body) if body else {}

    async def new_stream():
        yield body

    return Request(request.scope, receive=new_stream()), json_body
