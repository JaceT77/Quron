import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.utils.i18n import FSMI18nMiddleware, I18n

from api import APIClient
from core import settings
from handlers import start_router, surahs_router

log: structlog.BoundLogger = structlog.get_logger(__name__)
i18n = I18n(path="locales", default_locale="en", domain="messages")


dp = Dispatcher()


def setup_dispatcher(_dp: Dispatcher) -> None:
    _dp["client"] = APIClient(base_url=settings.BASE_URL)
    _dp["log"] = log


def dp_inject_routers(_dp: Dispatcher) -> None:
    _dp.include_router(start_router)
    _dp.include_router(surahs_router)


def dp_inject_middlewares(_dp: Dispatcher) -> None:
    _dp.update.middleware(FSMI18nMiddleware(i18n))


async def run() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        ),
    )
    try:
        me = await bot.get_me()
        log.info("bot_authorized", id=me.id, username=me.username)

        used_updates = dp.resolve_used_update_types()
        log.info("polling_starting", allowed_updates=used_updates)

        setup_dispatcher(dp)
        dp_inject_routers(dp)
        dp_inject_middlewares(dp)

        await dp.start_polling(bot, allowed_updates=used_updates)
    except TelegramUnauthorizedError:
        log.error("bot_token_invalid")
        raise
    except TelegramNetworkError:
        log.exception("telegram_unreachable")
        raise
    except Exception:
        log.exception("bot_crashed")
        raise
    finally:
        log.info("bot_stopping")
        await bot.close()
        log.info("bot_stopped")
