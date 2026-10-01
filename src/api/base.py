from typing import Any, TypeVar

import httpx2
from httpx2._client import AsyncClient
from httpx2._models import Response
from pydantic import BaseModel, TypeAdapter

T = TypeVar(name="T", bound=BaseModel)


class BaseService:
    base_path: str = ""

    def __init__(self, client: httpx2.AsyncClient):
        self._client: AsyncClient = client

    def _resolve_url(self, path: str) -> str:
        clean_base: str = self.base_path.strip("/")
        clean_sub: str = path.strip("/")
        joined: str = f"{clean_base}/{clean_sub}" if clean_sub else clean_base
        return f"/{joined}" if joined else "/"

    async def _request(
        self,
        method: str,
        path: str,
        response_model: type[T],
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> T:
        full_path: str = self._resolve_url(path)
        response: Response = await self._client.request(
            method=method, url=full_path, params=params, json=json
        )
        response.raise_for_status()
        return response_model.model_validate_json(json_data=response.content)

    async def _request_list(
        self,
        method: str,
        path: str,
        adapter: TypeAdapter[list[T]],
        *,
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        full_path: str = self._resolve_url(path)
        response: Response = await self._client.request(
            method=method, url=full_path, params=params
        )
        response.raise_for_status()
        return adapter.validate_json(response.content)
