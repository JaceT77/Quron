from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path: Path = Path.joinpath(Path.cwd(), ".env")


class Editions(BaseSettings):
    AR_AUDIO: str = "ar.alafasy"
    AR_TEXT: str = "ar.alafasy"
    EN_AUDIO: str = "en.misharyrashidalafasyenglishtranslationsaheehibrahimwalk"
    EN_TEXT: str = "en.ahmedali"
    EN_TRANSLITERATION: str = "en.transliteration"
    RU_AUDIO: str = "ru.kuliev-audio"
    RU_TEXT: str = "ru.kuliev"
    RU_TRANSLITERATION: str = "ru.transliteration"
    UZ_TEXT: str = "uz.sodik"
    UZ_AUDIO: str = "uz.sodik-audio"


class Settings(BaseSettings):
    ADMIN: int
    BASE_URL: str = "https://api.alquran.cloud/v1/"
    BOT_TOKEN: SecretStr
    DEBUG: bool = True

    editions: Editions = Editions()

    model_config = SettingsConfigDict(env_file=env_path)
