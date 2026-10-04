import shlex

import httpx2

from api.service import AyahService, PageService, SurahService
from core import settings


async def curl_logger(request: httpx2.Request) -> None:
    parts = ["curl -X", request.method, shlex.quote(str(request.url))]

    # Add HTTP/2 flag if desired
    # parts.append("--http2")

    # Add headers
    for key, value in request.headers.items():
        # Exclude internal/pseudo or redundant headers if preferred
        parts.extend(["-H", shlex.quote(f"{key}: {value}")])

    # Add request body/payload if present
    if request.content:
        try:
            body = request.content.decode("utf-8")
        except UnicodeDecodeError:
            body = "<binary data>"
        parts.extend(["--data-raw", shlex.quote(body)])

    print("\n" + " ".join(parts) + "\n")


class APIClient:
    surah: SurahService
    ayah: AyahService
    page: PageService

    def __init__(
        self,
        base_url: str = settings.BASE_URL,
        api_key: str | None = None,
        timeout: float = 10.0,
    ):
        headers: dict[str, str] = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._http_client = httpx2.AsyncClient(
            base_url=base_url,
            timeout=httpx2.Timeout(timeout),
            headers=headers,
            event_hooks={
                "request": [curl_logger],
            },
        )

        # Wire up modular sections
        self.surah = SurahService(self._http_client)
        self.ayah = AyahService(self._http_client)
        self.page = PageService(self._http_client)

    async def aclose(self) -> None:
        await self._http_client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
