from typing import Literal

import structlog
from httpx2 import HTTPError

from api.base import BaseService
from core import settings
from schemas import schemas

log: structlog.BoundLogger = structlog.get_logger()

Lang = Literal["ar", "en", "ru", "uz"]
Kind = Literal["text", "audio", "transliteration"]


def choose_edition(
    ft: Kind = "text",
    ln: Lang = "ar",
) -> str:
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
            ("uz", "transliteration"): e.EN_TRANSLITERATION,
        }

    try:
        return _edition_table()[(ln, ft)]
    except KeyError:
        raise ValueError(
            f"No edition configured for language={ln!r}, type={ft!r}"
        ) from None


class SurahService(BaseService):
    base_path: str = "/surah/"

    async def list(self) -> schemas.SurahList:
        """
        List surahs
        :return: SurahList
        """
        try:
            log.debug(event="Retrieving list of surahs")
            response = await self._request(
                method="GET",
                path="",
                response_model=schemas.SurahList,
            )
        except HTTPError as err:
            log.exception(
                event="HTTPError occured while retrieving surah list",
                response=err,
            )
            raise HTTPError from err
        else:
            log.debug(event="Surah list", response=response)
            log.info(event="Retrieved list of surahs")
            return response

    async def get(
        self,
        surah_number: int,
        ft: Kind = "text",
        ln: Lang = "ar",
    ) -> schemas.Surah:
        """
        Get a surah with edition
        :param surah_number: Surah number
        :param ft: text, audio, transliteration
        :param ln: ar, ru, uz, en
        :return: SurahList
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            log.debug(
                event="Retrieving a surah",
                surah_number=surah_number,
            )
            response = await self._request(
                method="GET",
                path=f"{surah_number}/{edition}",
                response_model=schemas.Surah,
            )
        except HTTPError as err:
            log.exception(
                event="HTTPError occured while retrieving surah",
                surah_number=surah_number,
                response=err,
            )
            raise HTTPError from err
        else:
            log.debug(
                event="Surah",
                format=ft,
                language=ln,
                surah_number=surah_number,
                response=response,
            )
            log.info(
                event="Retrieved surah",
                surah_number=surah_number,
            )
            return response


class AyahService(BaseService):
    base_path: str = "/ayah/"

    async def get(
        self,
        surah_number: int,
        ayah_number: int,
        ft: Kind = "text",
        ln: Lang = "ar",
    ) -> schemas.Ayah:
        """
        Get an ayah with edition
        :param surah_number:
        :param ayah_number:
        :param ft:
        :param ln:
        :return: Ayah
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            log.debud(
                event="Retrieving ayah from surah",
                surah_number=surah_number,
                ayah_number=ayah_number,
            )
            response = await self._request(
                method="GET",
                path=f"/{surah_number}:{ayah_number}/{edition}",
                response_model=schemas.Ayah,
            )
        except HTTPError as err:
            log.exception(event="HTTPError occured while retrieving ayah", response=err)
            raise HTTPError from err
        else:
            log.debug(
                event="Retrieved ayah from surah",
                response=response,
                surah_number=surah_number,
                ayah_number=ayah_number,
            )
            log.info(
                event="Retrieved ayah from surah",
                surah_number=surah_number,
                ayah_number=ayah_number,
            )
            return response

    async def get_by_order(
        self,
        ayah_order: int,
        ft: Kind = "text",
        ln: Lang = "ar",
    ) -> schemas.Ayah:
        """
        Get an ayah with order number without surah
        :param ayah_order:
        :param ft:
        :param ln:
        :return: Ayah
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            log.debug(event="Retrieving ayah by order")
            response = await self._request(
                method="GET",
                path=f"/{ayah_order}/{edition}",
                response_model=schemas.Ayah,
            )
        except HTTPError as err:
            log.exception(
                event="HTTPError occured while retrieving ayah by order",
                ayah_order=ayah_order,
                err=err,
            )
            raise HTTPError from err
        else:
            log.debug(
                event="Retrieved Ayah by order",
                ayah_order=ayah_order,
                response=response,
            )
            log.info(event="Retrieved Ayah by order", ayah_order=ayah_order)
            return response


class PageService(BaseService):
    base_path: str = "/page/"

    async def get(
        self,
        page_number: int = 1,
        ft: Kind = "text",
        ln: Lang = "ar",
    ) -> schemas.Page:
        """
        Get a page with edition
        :param page_number:
        :param ft: text, audio, transliteration
        :param ln: ar, ru, uz, en
        :return: Page
        """
        edition = choose_edition(ft=ft, ln=ln)
        try:
            log.debug(event="Retrieving page", page_number=page_number)
            response = await self._request(
                method="GET",
                path=f"/{page_number}/{edition}",
                response_model=schemas.Page,
            )
        except HTTPError as err:
            log.exception(
                event="HTTPError occured while getting page",
                page_number=page_number,
                response=err,
            )
            raise HTTPError from err
        else:
            log.debug(
                event="Retrieved page",
                page_number=page_number,
                response=response,
            )
            log.info(event="Retrieved page", page_number=page_number)
            return response
