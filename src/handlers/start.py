from aiogram import F, Router, html
from aiogram import types as t
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n import gettext as _

from keyboards.inline import inline_kbs

router = Router()


@router.callback_query(F.data == "start")
@router.message(Command("start"))
async def start(event: t.CallbackQuery | t.Message, state: FSMContext):
    user: t.User | None = event.from_user
    if user is None:
        return

    if isinstance(event, t.CallbackQuery):
        await event.answer()  # dismiss the loading spinner
        msg: t.Message | t.InaccessibleMessage | None = event.message
        if not isinstance(msg, t.Message):
            return  # inaccessible or None: nothing we can reply to
    else:
        msg: t.Message = event

    await msg.answer(
        text=_("Hello, {name}!").format(name=html.bold(value=user.first_name)),
        reply_markup=inline_kbs.home_menu_kb(),
    )


@router.message(Command("help"))
async def help(msg: t.Message):
    await msg.answer(text="/start")


@router.callback_query(F.data == "change_language")
async def lang(cb: t.CallbackQuery):
    if not isinstance(cb, t.CallbackQuery) or not isinstance(cb.message, t.Message):
        return

    await cb.message.answer(
        text=_("Choose your language!"), reply_markup=inline_kbs.get_language_kb(),
    )


@router.callback_query(inline_kbs.ChangeLang.filter())
async def change_lang(
    cb: t.CallbackQuery,
    callback_data: inline_kbs.ChangeLang,
    state: FSMContext,
    i18n: I18n,
):
    await state.update_data(locale=callback_data.lang)
    i18n.current_locale = callback_data.lang
    await cb.answer()
    await cb.answer(text=_("Your new language"))


@router.callback_query(F.data.startswith("quran"))
async def quran(cb: t.CallbackQuery):
    if not isinstance(cb, t.CallbackQuery) or not isinstance(cb.message, t.Message):
        return
    await cb.message.edit_text(
        text=_("What would you like to read?"),
        reply_markup=inline_kbs.read_quran_kb(),
    )
