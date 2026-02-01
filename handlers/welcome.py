from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from utils.http_client import get_session

from datetime import datetime
import pytz, os

router = APIRouter()
# router = APIRouter(prefix="/skill")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def time_to_cn(dt: datetime):
    period = "上午" if dt.hour < 12 else "下午"
    hour = dt.hour if dt.hour <= 12 else dt.hour - 12
    minute = dt.minute
    return f"{dt.month}月{dt.day}日，{period}{hour}点{minute}分"

WIND_DIR_MAP = {
    "N": "北",
    "NNE": "北偏东",
    "NE": "东北偏北",
    "ENE": "东偏北",
    "E": "东",
    "ESE": "东偏南",
    "SE": "东南偏东",
    "SSE": "南偏东",
    "S": "南",
    "SSW": "南偏西",
    "SW": "西南偏南",
    "WSW": "西偏南",
    "W": "西",
    "WNW": "西偏北",
    "NW": "西北偏西",
    "NNW": "北偏西"
}
def parse_slots(data: dict, slot_name: str, default_value: str) -> dict:
    slots = {
        slot.get("intentParameterName"): slot.get("standardValue")
        for slot in data
        if slot.get("intentParameterName") and slot.get("standardValue")
    }
    return slots.get(slot_name, default_value)
        
def format_weather_reply(city: str, data: dict) -> str:
    """把 WeatherAPI JSON 转成中文播报"""
    try:
        current = data["current"]
        condition = current["condition"]["text"]
        temp_c = current["temp_c"]
        feelslike = current.get("feelslike_c", temp_c)
        wind_kph = current.get("wind_kph", "")
        humidity = current.get("humidity", "")
        wind_dir_en = current.get("wind_dir", "")
        wind_dir_cn = WIND_DIR_MAP.get(wind_dir_en, wind_dir_en)
        reply = (
            f"{city}现在天气{condition}，气温{temp_c:.1f}°C，体感温度{feelslike:.1f}°C，"
            f"风向{wind_dir_cn}，风速每小时{wind_kph}公里，湿度{humidity}%。"
        )
        return reply
    except Exception as e:
        return f"抱歉，无法解析{city}的天气信息。"
async def get_weather():
    session = await get_session()
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": os.getenv("WEATHER_API_KEY", ""),
        "q": "willowdale",
        "lang": "zh"  # 返回中文描述
    }
    async with session.get(url, params=params, timeout=5) as resp:
        return await resp.json()

@router.post("/skill/welcome")
async def welcome(req: Request):
    body = await req.json()
    req.state.logger.info(f"skill_welcome req: {body}")
    action = parse_slots(body.get("slotEntities", []), "action", "时间")
    reply = ""
    if action == "时间":
        tz = pytz.timezone("America/Toronto")
        now = datetime.now(tz)
        time_str = now.strftime("%m月%d日 %H:%M")
        reply = f"现在是多伦多时间，{time_str}。"
    elif action == "天气":
        try:
            weather_data = await get_weather()
            reply = format_weather_reply("willowdale", weather_data)
        except Exception as e:
            req.state.logger.info(f"天气查询失败: {str(e)}")
            reply = f"天气信息暂时不可用"
    else:
        reply = f"抱歉，我不理解你说的请求 {action}"
    
    return JSONResponse({
        "returnCode": "0",
        "returnErrorSolution": "",
        "returnMessage": "",
        "returnValue": {
            "reply": reply,
            "resultType": "RESULT",
            "executeCode": "SUCCESS"
        }
    })

@router.get("/aligenie/{name}", response_class=PlainTextResponse)
def get_auth_file(name: str):
    file_path = os.path.join(os.path.join(BASE_DIR, "authfile"), name)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="auth file not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()