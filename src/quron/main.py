from pprint import pprint as print

from api.client import APIClient
from core import settings


async def run():
    async with APIClient(base_url=settings.BASE_URL) as client:
        l = await client.page.get(page=2, ft="text", ln="uz")
        print(l)
