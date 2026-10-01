from __future__ import annotations

from pydantic import BaseModel


class Edition(BaseModel):
    identifier: str
    language: str
    name: str
    englishName: str
    format: str
    type: str
    direction: str | None = None


class AyahDetail(BaseModel):
    number: int
    audio: str | None = (
        None
    )
    audioSecondary: list[str] | None = (
        None
    )
    text: str
    numberInSurah: int
    juz: int
    manzil: int
    page: int
    ruku: int
    hizbQuarter: int
    sajda: bool | dict | None = False
    edition: Edition | None = None
    surah: SurahDetail | None = None


class Ayah(BaseModel):
    code: int
    status: str
    data: AyahDetail


class SurahDetail(BaseModel):
    number: int | None = None
    name: str
    englishName: str
    englishNameTranslation: str
    numberOfAyahs: int
    revelationType: str
    ayahs: list[AyahDetail] | None = None
    edition: Edition | None = None



AyahDetail.model_rebuild()
SurahDetail.model_rebuild()


class SurahList(BaseModel):
    code: int
    status: str
    data: list[SurahDetail]


class Surah(BaseModel):
    code: int
    status: str
    data: SurahDetail


class PageDetail(BaseModel):
    number: int
    ayahs: list[AyahDetail]
    surahs: dict[int, SurahDetail]
    edition: Edition | None = None


class Page(BaseModel):
    code: int
    status: str
    data: PageDetail
