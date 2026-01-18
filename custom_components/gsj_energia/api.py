import aiohttp
from yarl import URL


class GSJClient:
    def __init__(self, host, username, password, device_id):
        self._host = host
        self._username = username
        self._password = password
        self._device_id = device_id
        self._csrf_token = None
        self._session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True))

    async def close(self):
        await self._session.close()

    async def login(self):
        base = f"http://{self._host}"

        # 1. Pobierz cookie CSRF z Sanctum
        async with self._session.get(f"{base}/sanctum/csrf-cookie") as resp:
            cookies = self._session.cookie_jar.filter_cookies(URL(base))
            if "XSRF-TOKEN" not in cookies:
                raise Exception("Brak XSRF-TOKEN z /sanctum/csrf-cookie")
            self._csrf_token = cookies["XSRF-TOKEN"].value

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": base,
        }

        data = {
            "_token": self._csrf_token,
            "username": self._username,
            "password": self._password,
        }

        # 2. Logowanie
        async with self._session.post(
            f"{base}/login",
            data=data,
            headers=headers,
            allow_redirects=False,
        ) as resp:
            if resp.status not in (200, 302):
                raise Exception(f"Błąd logowania, HTTP {resp.status}")

        # 3. Sprawdzenie sesji
        cookies = self._session.cookie_jar.filter_cookies(URL(base))
        if "gsj_session" not in cookies:
            raise Exception("Brak gsj_session po logowaniu")

    async def set_value(self, key, value):
        url = f"http://{self._host}/set-user-cache"
        params = {
            "deviceId": self._device_id,
            "key": key,
            "value": value,
        }

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"http://{self._host}/",
        }

        async with self._session.post(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd zapisu {key}={value}, HTTP {resp.status}")

    async def get_value(self, key):
        url = f"http://{self._host}/get-user-cache"
        params = {
            "deviceId": self._device_id,
            "key": key,
        }

        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Błąd odczytu {key}, HTTP {resp.status}")
            return (await resp.text()).strip()
