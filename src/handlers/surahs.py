import time
from typing import Any

from aiogram import F, Router, exceptions
from aiogram import types as t
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from structlog import BoundLogger

from api import APIClient
from api.service import Lang
from keyboards.inline import inline_kbs
from schemas import schemas

router = Router()


def _elapsed_ms(started: float) -> float:
    return round(number=(time.perf_counter() - started) * 1000, ndigits=1)


@router.callback_query(inline_kbs.PagingCB.filter(rule=F.kb_for == "surah"))
async def list_surahs(
    cb: t.CallbackQuery,
    callback_data: inline_kbs.PagingCB,
    client: APIClient,
    log: BoundLogger,
):
    log: BoundLogger = log.bind(
        handler="list_surahs",
        user_id=cb.from_user.id,
        start=callback_data.start,
    )
    log.debug("handler_called", raw_data=cb.data)

    if not isinstance(cb.message, t.Message):
        log.warning(
            "message_inaccessible",
            message_type=type(cb.message).__name__,
        )
        await cb.answer()
        return

    log = log.bind(chat_id=cb.message.chat.id, message_id=cb.message.message_id)

    try:
        started: float | int = time.perf_counter()
        log.debug("fetching_surah_list")
        response: schemas.SurahList = await client.surah.list()
        log.debug(
            "surah_list_fetched",
            count=len(response.data),
            elapsed_ms=_elapsed_ms(started),
        )

        kb: InlineKeyboardMarkup = inline_kbs.get_surah_list_kb(
            surahs=response.data, start=callback_data.start
        )

        if cb.message.audio is not None:
            log.debug("message_has_audio", action="delete_and_resend")
            await cb.message.delete()
            await cb.message.answer(text=_("Surah list"), reply_markup=kb)
        else:
            log.debug("message_is_text", action="edit_text")
            await cb.message.edit_text(text=_("List of surahs"), reply_markup=kb)

        await cb.answer()  # stops the loading spinner
        log.debug("surah_list_sent")

    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(object=e):
            log.debug("message_not_modified", detail="user pressed the same page")
            await cb.answer()
            return
        log.exception("telegram_bad_request", error=str(object=e))
        await cb.answer(text=_("Problem with getting surahs. Try again"))
    except Exception:
        log.exception("surah_list_failed")
        await cb.answer(text=_("Problem with getting surahs. Try again"))


async def send_ayah(
    state: FSMContext,
    cb: t.CallbackQuery,
    client: APIClient,
    log: BoundLogger,
    surah_number: int | None = None,
    ayah_number: int | None = None,
    ayah_order: int | None = None,
) -> None:
    """
    Sends an ayah (audio + Arabic text, transliteration and translation).

    :param state: FSM context holding the user's locale
    :param cb: the callback query that triggered the request
    :param client: API client
    :param log: structlog logger
    :param surah_number: surah number (used together with ayah_number)
    :param ayah_number: ayah number inside the surah
    :param ayah_order: absolute ayah order (1..6236), used if no surah/ayah pair
    """
    log = log.bind(
        handler="send_ayah",
        user_id=cb.from_user.id,
        surah_number=surah_number,
        ayah_number=ayah_number,
        ayah_order=ayah_order,
    )
    log.debug("handler_called", raw_data=cb.data)

    if not isinstance(cb.message, t.Message):
        log.warning(
            "message_inaccessible",
            message_type=type(cb.message).__name__,
        )
        await cb.answer()
        return

    log = log.bind(chat_id=cb.message.chat.id, message_id=cb.message.message_id)

    data: dict[str, Any] = await state.get_data()
    lang: Lang | None = data.get("locale")
    log.debug("state_loaded", state_keys=list(data.keys()), lang=lang)
    if lang is None:
        log.error("locale_missing_in_state", state_keys=list(data.keys()))
        await cb.answer(text=_("Problem with getting surahs. Try again"))
        return

    log.debug("deleting_previous_message")
    await cb.message.delete()

    try:
        started: float | int = time.perf_counter()

        if surah_number and ayah_number:
            log.debug("fetching_ayah", mode="by_surah_and_ayah", lang=lang)
            ar: schemas.Ayah = await client.ayah.get(
                surah_number=surah_number,
                ayah_number=ayah_number,
                ft="audio",
            )
            log.debug("ayah_fetched", part="audio")
            tr: schemas.Ayah = await client.ayah.get(
                surah_number=surah_number,
                ayah_number=ayah_number,
                ln=lang,
                ft="transliteration",
            )
            log.debug("ayah_fetched", part="transliteration")
            l: schemas.Ayah = await client.ayah.get(
                surah_number=surah_number,
                ayah_number=ayah_number,
                ln=lang,
            )
            log.debug("ayah_fetched", part="translation")
        elif ayah_order:
            log.debug("fetching_ayah", mode="by_order", lang=lang)
            ar: schemas.Ayah = await client.ayah.get_by_order(
                ayah_order=ayah_order,
                ft="audio",
            )
            log.debug("ayah_fetched", part="audio")
            tr: schemas.Ayah  = await client.ayah.get_by_order(
                ayah_order=ayah_order,
                ln=lang,
                ft="transliteration",
            )
            log.debug("ayah_fetched", part="transliteration")
            l: schemas.Ayah  = await client.ayah.get_by_order(
                ayah_order=ayah_order,
                ln=lang,
            )
            log.debug("ayah_fetched", part="translation")
        else:
            log.error("no_ayah_identifier_given")
            await cb.answer(text=_("Problem with getting surahs. Try again"))
            return

        log.debug("all_ayah_parts_fetched", elapsed_ms=_elapsed_ms(started))

        ayah: schemas.AyahMessage = schemas.AyahMessage(
            number=ar.data.number,
            ar=ar.data.text,
            tr=tr.data.text,
            l=l.data.text,
            audio=ar.data.audio or "",
            numberInSurah=ar.data.numberInSurah,
            juz=ar.data.juz,
            manzil=ar.data.manzil,
            page=ar.data.page,
            ruku=ar.data.ruku,
            hizbQuarter=ar.data.hizbQuarter,
            surah_number=ar.data.surah.number or 0,
            surah_name=ar.data.surah.englishName,
        )
        log.debug(
            "ayah_message_built",
            number=ayah.number,
            number_in_surah=ayah.numberInSurah,
            surah_name=ayah.surah_name,
            has_audio=bool(ayah.audio),
        )
        if not ayah.audio:
            log.warning("ayah_has_no_audio_url")

        text = f"""{ayah.numberInSurah}. {ayah.surah_name}
        {ayah.ar}

        {ayah.tr}

        {ayah.l}
"""
        log.debug("caption_built", caption_length=len(text))

        await cb.message.answer_audio(
            audio=ayah.audio,
            caption=text,
            reply_markup=inline_kbs.get_ayah_detail_kb(
                ayah_order=ayah.number, surah=ayah.surah_number
            ),
        )
        await cb.answer()
        log.debug("ayah_sent", total_elapsed_ms=_elapsed_ms(started))

    except exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(object=e):
            log.debug("message_not_modified")
            await cb.answer()
            return
        log.exception("telegram_bad_request", error=str(object=e))
        await cb.answer(text=_("Problem with getting surahs. Try again"))
    except Exception:
        log.exception("send_ayah_failed")
        await cb.answer(text=_("Problem with getting surahs. Try again"))


@router.callback_query(inline_kbs.ChooseAyah.filter())
async def read_ayahs_by_order(
    cb: t.CallbackQuery,
    callback_data: inline_kbs.ChooseAyah,
    state: FSMContext,
    client: APIClient,
    log: BoundLogger,
):
    log.debug(
        "handler_called",
        handler="read_ayahs_by_order",
        user_id=cb.from_user.id,
        ayah_order=callback_data.ayah_order,
    )
    await send_ayah(
        state=state,
        cb=cb,
        client=client,
        log=log,
        ayah_order=callback_data.ayah_order,
    )


@router.callback_query(inline_kbs.ChooseSurah.filter())
async def read_surah(
    cb: t.CallbackQuery,
    callback_data: inline_kbs.ChooseSurah,
    state: FSMContext,
    client: APIClient,
    log: BoundLogger,
):
    log.debug(
        "handler_called",
        handler="read_surah",
        user_id=cb.from_user.id,
        surah_number=callback_data.surah_number,
        ayah_number=callback_data.ayah_number,
    )
    await send_ayah(
        state=state,
        cb=cb,
        client=client,
        log=log,
        surah_number=callback_data.surah_number,
        ayah_number=callback_data.ayah_number,
    )