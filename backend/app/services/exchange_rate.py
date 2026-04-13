import httpx
from datetime import datetime

FRANKFURTER_URL = "https://api.frankfurter.app"

async def get_exchange_rate(date: str = "latest") -> float:
    url = f"{FRANKFURTER_URL}/{date}?from=USD&to=GTQ"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        return data["rates"]["GTQ"]