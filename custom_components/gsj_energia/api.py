import aiohttp


class GSJClient:
    def __init__(self, host, username, password, device_id):
        self._host = host
        self._username = username
        self._password = password
        self._device_id = device_id
        self._session = aiohttp.ClientSession()
        self._csrf_token = None

    async def close(self):
        await self._session.close()

    async def login(self):
        # 1. Wejście na stronę główną – serwer ustawia XSRF-TOKEN
        async with self._session.get(f"http://{self._host}/") as resp:
            cookies = resp.cookies
            if "XSRF-TOKEN" not in cookies:
                raise Exception("Nie znaleziono XSRF-TOKEN po GET /")
            self._csrf_token = cookies["XSRF-TOKEN"].value

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"http://{self._host}/",
        }

        data = {
            "_token": self._csrf_token,
            "username": self._username,
            "password": self._password,
        }

        # 2. Logowanie właściwe
        async with self._session.post(
            f"http://{self._host}/login",
            data=data,
            headers=headers,
            allow_redirects=False,
        ) as resp:
            if resp.status not in (200, 302):
                raise Exception(f"Błąd logowania, HTTP {resp.status}")

        # 3. Sprawdzenie czy sesja powstała
        cookies = self._session.cookie_jar.filter_cookies(f"http://{self._host}")
        if "gsj_session" not in cookies:
            raise Exception("Brak ciasteczka gsj_session – logowanie nieudane")

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
