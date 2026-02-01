import aiohttp, json
from fastapi import Request

session: aiohttp.ClientSession | None = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

async def request_summary(request: Request) -> str:
    body = ""
    try:
        raw = await request.body()
        if raw:
            body = raw.decode("utf-8")
    except Exception:
        pass

    return (
        f"{request.client.host if request.client else '-'}, "
        f"{request.headers.get('X-Forwarded-For', '')}, "
        f"{request.url.path}, "
        f"{request.method}, "
        f"query={dict(request.query_params)}, "
        f"body={body}"
    )

def parse_slots(data: dict) -> dict:
    slots = {}
    for slot in data.get("slotEntities", []):
        name = slot.get("slotName")
        value = slot.get("slotValue")
        if name and value:
            slots[name] = value
    return slots