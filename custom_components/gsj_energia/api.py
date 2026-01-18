import aiohttp
from yarl import URL


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
        base_url = f"http://{self._host}"

        # 1. Pobierz stronę główną aby dostać XSRF-TOKEN
        async with self._session.get(base_url) as resp:
            cookies = resp.cookies
            if "XSRF-TOKEN" not in cookies:
                raise Exception("Brak XSRF-TOKEN po GET /")

            self._csrf_token = cookies["XSRF-TOKEN"].value

            # Wstawiamy cookie ręcznie do cookie_jar (ważne!)
            self._session.cookie_jar.update_cookies(
                {"XSRF-TOKEN": self._csrf_token},
                response_url=URL(base_url),
            )

        headers = {
            "X-CSRF-TOKEN": self._csrf_token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": base_url,
        }

        data = {
            "_token": self._csrf_token,
            "username": self._username,
            "password": self._password,
        }

        # 2. Właściwe logowanie
        async with self._session.post(
            f"{base_url}/login",
            data=data,
            headers=headers,
            allow_redirects=False,
        ) as resp:
            if resp.status not in (200, 302):
                raise Exception(f"Błąd logowania, HTTP {resp.status}")

        # 3. Sprawdzenie sesji
        cookies = self._session.cookie_jar.filter_cookies(URL(base_url))
        if "gsj_session" not in cookies:
            raise Exception("Brak cookie gsj_session – logowanie nieudane")

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
