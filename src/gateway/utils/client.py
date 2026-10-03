import httpx
from typing import Any, Dict, Optional

class MicroserviceClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            follow_redirects=False,
            headers=self.default_headers,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Универсальный метод запроса с обработкой ошибок."""
        url = path.lstrip("/")
        try:
            response = await self._client.request(method, url, json=json_data, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            raise
        except httpx.RequestError as e:
            raise

    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, json_data: Any, **kwargs) -> Dict[str, Any]:
        return await self.request("POST", path, json_data=json_data, **kwargs)

    async def put(self, path: str, json_data: Any, **kwargs) -> Dict[str, Any]:
        return await self.request("PUT", path, json_data=json_data, **kwargs)

    async def patch(self, path: str, json_data: Any, **kwargs) -> Dict[str, Any]:
        return await self.request("PATCH", path, json_data=json_data, **kwargs)

    async def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        return await self.request("DELETE", path, **kwargs)