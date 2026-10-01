from typing import Literal

import structlog
from httpx2 import _exceptions

from api.base import BaseService
from core import settings
from schemas import schemas

log: structlog.BoundLogger = structlog.get_logger()



Lang = Literal["ar", "en", "ru", "uz"]
Kind = Literal["text", "audio", "transliteration"]


def _edition_table() -> dict[tuple[str, str], str]:
    e = settings.editions
    return {
        ("ar", "text"): e.AR_TEXT,
        ("ar", "audio"): e.AR_AUDIO,
        ("en", "text"): e.EN_TEXT,
        ("en", "audio"): e.EN_AUDIO,
        ("en", "transliteration"): e.EN_TRANSLITERATION,
        ("ru", "text"): e.RU_TEXT,
        ("ru", "audio"): e.RU_AUDIO,
        ("ru", "transliteration"): e.RU_TRANSLITERATION,
        ("uz", "text"): e.UZ_TEXT,
        ("uz", "audio"): e.UZ_AUDIO,
    }


def choose_edition(ft: Kind = "text", ln: Lang = "ar") -> str:
    try:
        return _edition_table()[(ln, ft)]
    except KeyError:
        raise ValueError(f"No edition configured for language={ln!r}, type={ft!r}") from None


class SurahService(BaseService):
    base_path: str = "/surah/"

    async def list(self) -> schemas.SurahList:
        """
        List surahs
        :return: SurahList
        """
        try:
            response = self._request(
                method="GET",
                path="",
                response_model=schemas.SurahList
            )
        except _exceptions.HTTPError as err:
            log.exception(event="Surah list", response=err)
            raise _exceptions.HTTPError from err
        else:
            log.info(event="Surah list", response=response)
            return response

    async def get(self, surah: int, ft: str = "text", ln: str = "ar") -> schemas.Surah:
        """
        Get a surah with edition
        :param number: Surah number
        :param ft: text, audio, transliteration
        :param ln: ar, ru, uz, en
        :return: SurahList
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            response = await self._request(
                method="GET",
                path=f"{surah}/{edition}",
                response_model=schemas.Surah
            )
        except _exceptions.HTTPError as err:
            log.exception(event="Surah", response=err)
            raise _exceptions.HTTPError from err
        else:
            log.info(event="Surah", format=ft, language=ln, surah=surah, response=response)
            return response


class AyahService(BaseService):
    base_path: str = "/ayah/"

    async def get(self, surah: int, verse: int, ft: str = "text", ln: str = "ar") -> schemas.Ayah:
        """
        Get an ayah with edition
        :param surah:
        :param verse:
        :param ft:
        :param ln:
        :return: Ayah
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            response = await self._request(
                method="GET",
                path=f"/{surah}:{verse}/{edition}",
                response_model=schemas.Ayah
            )
        except _exceptions.HTTPError as err:
            log.exception(event="Ayah", response=err)
            raise _exceptions.HTTPError from err
        else:
            log.info(event="Ayah", response=response)
            return response

class PageService(BaseService):
    base_path: str = "/page/"

    async def get(self, page: int = 1, ft: str = "text", ln: str = "ar") -> schemas.Page:
        """
        Get a page with edition
        :param page:
        :param ft: text, audio, transliteration
        :param ln: ar, ru, uz, en
        :return: Page
        """
        edition = choose_edition(ft="text", ln="ar")
        try:
            response = await self._request(
                method="GET",
                path=f"/{page}/{edition}",
                response_model=schemas.Page
            )
        except _exceptions.HTTPError as err:
            log.exception(event="Page", response=err)
            raise _exceptions.HTTPError from err
        else:
            log.info(event="Page", response=response)
            return response
