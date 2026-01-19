import aiohttp
from typing import Dict


class GSJClient:
    def __init__(self, base_url: str = "http://localhost:8124"):
        self._base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def async_init(self):
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)

    async def async_close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def get_status(self) -> Dict:
        await self.async_init()
        url = f"{self._base_url}/sensors"

        async with self._session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd odczytu z GSJ Browser API: HTTP {resp.status}")
            return await resp.json()

    async def set_value(self, key: str, value):
        await self.async_init()
        url = f"{self._base_url}/set"

        payload = {
            "key": key,
            "value": value
        }

        async with self._session.post(url, json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd zapisu do GSJ Browser API: HTTP {resp.status}")
            return await resp.json()
