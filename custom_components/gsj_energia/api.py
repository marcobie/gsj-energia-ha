import aiohttp
from http.cookies import SimpleCookie
from urllib.parse import urljoin

class GSJClient:
    def __init__(self, host, username, password, device_id):
        self._host = host
        self._username = username
        self._password = password
        self._device_id = device_id
        self._session = aiohttp.ClientSession()
        self._cookies = {}
        self._csrf_token = None

    async def close(self):
        await self._session.close()

    async def login(self):
        # Pobierz stronę logowania aby dostać XSRF-TOKEN
        async with self._session.get(f"http://{self._host}/") as resp:
            cookies = resp.cookies
            if "XSRF-TOKEN" in cookies:
                self._csrf_token = cookies["XSRF-TOKEN"].value

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
        }

        data = {
            "_token": self._csrf_token,
            "username": self._username,
            "password": self._password,
        }

        async with self._session.post(
            f"http://{self._host}/login",
            data=data,
            headers=headers,
            allow_redirects=False,
        ) as resp:
            if resp.status not in (200, 302):
                raise Exception("Błąd logowania do GSJ Energia")

        # Zapisz cookies sesji
        self._cookies = self._session.cookie_jar.filter_cookies(f"http://{self._host}")

    async def set_value(self, key, value):
        if not self._csrf_token:
            await self.login()

        url = f"http://{self._host}/set-user-cache"
        params = {
            "deviceId": self._device_id,
            "key": key,
            "value": value,
        }

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
        }

        async with self._session.post(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd zapisu {key}={value}")

    async def get_value(self, key):
        url = f"http://{self._host}/get-user-cache"
        params = {
            "deviceId": self._device_id,
            "key": key,
        }

        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd odczytu {key}")
            return await resp.text()
