from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from schemas import schemas

PAGE_SIZE = 10


class PagingCB(CallbackData, prefix="PagingCB"):
    kb_for: str
    start: int


class ChangeLang(CallbackData, prefix="ChangeLang"):
    lang: str


class ChooseSurah(CallbackData, prefix="ChooseSurah"):
    surah_number: int
    ayah_number: int


class ChooseAyah(CallbackData, prefix="ChooseAyah"):
    ayah_order: int


def _build_kb(
    buttons: list[dict[str, str]], back: str | None = None, add_home: bool = True
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    [
        builder.add(InlineKeyboardButton(text=item["text"], callback_data=item["cd"]))
        for item in buttons
    ]

    nav = InlineKeyboardBuilder()
    if back:
        nav.add(InlineKeyboardButton(text=_("Back"), callback_data=back))
    if add_home:
        nav.add(InlineKeyboardButton(text=_("Home"), callback_data="start"))
    nav.adjust(2, 1)
    builder.attach(nav)
    return builder.as_markup()


def _back_and_home_nav() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=_("Back"), callback_data="quran"))
    builder.add(InlineKeyboardButton(text=_("Home"), callback_data="start"))
    builder.adjust(2, 1)
    return builder


def _build_paging_kb(
    buttons: list[dict[str, str]], kb_for: str, start: int
) -> InlineKeyboardMarkup:
    # clamp and snap to a page boundary so a stale or odd value can't break anything
    start = max(0, min(start, len(buttons) - 1))
    start -= start % PAGE_SIZE

    builder = InlineKeyboardBuilder()
    for item in buttons[start : start + PAGE_SIZE]:  # slicing never overruns
        builder.button(text=item["text"], callback_data=item["cd"])
    builder.adjust(1)

    nav = InlineKeyboardBuilder()
    if start > 0:
        nav.add(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=PagingCB(kb_for=kb_for, start=(start - PAGE_SIZE)).pack(),
            )
        )
    if start + PAGE_SIZE < len(buttons):
        nav.add(
            InlineKeyboardButton(
                text="➡️",
                callback_data=PagingCB(kb_for=kb_for, start=(start + PAGE_SIZE)).pack(),
            )
        )
    nav.adjust(2, 1)
    builder.attach(nav)
    builder.attach(_back_and_home_nav())

    return builder.as_markup()


def home_menu_kb() -> InlineKeyboardMarkup:
    buttons: list[dict[str, str]] = [
        {"text": _("Read Qur'an📖"), "cd": "quran"},
        {"text": _("Set a reminder🔔"), "cd": "set_reminder"},
        {"text": _("Change language"), "cd": "change_language"},
    ]
    return _build_kb(buttons, add_home=False)


def read_quran_kb() -> InlineKeyboardMarkup:
    buttons: list[dict[str, str]] = [
        {"text": _("Surah"), "cd": PagingCB(kb_for="surah", start=0).pack()},
        {"text": _("Page"), "cd": PagingCB(kb_for="page", start=0).pack()},
    ]
    return _build_kb(buttons)


def get_language_kb() -> InlineKeyboardMarkup:
    buttons: list[dict[str, str]] = [
        {"text": "🇺🇿 O'zbekcha", "cd": ChangeLang(lang="uz").pack()},
        {"text": "🇷🇺 Русский", "cd": ChangeLang(lang="ru").pack()},
        {"text": "🇬🇧 English", "cd": ChangeLang(lang="en").pack()},
    ]
    return _build_kb(buttons)


def get_surah_list_kb(
    surahs: list[schemas.SurahDetail], start: int = 0
) -> InlineKeyboardMarkup:
    buttons: list[dict[str, str]] = []

    for surah in surahs:
        b = {
            "text": f"{surah.number}. {surah.englishName}",
            "cd": ChooseSurah(surah_number=surah.number or 0, ayah_number=1).pack(),
        }
        buttons.append(b)

    return _build_paging_kb(buttons, kb_for="surah", start=start)


def get_ayah_detail_kb(ayah_order: int, surah: int) -> InlineKeyboardMarkup:
    buttons: list[dict[str, str]] = []

    if ayah_order > 1:
        buttons.append(
            {"text": "⬅️", "cd": ChooseAyah(ayah_order=ayah_order - 1).pack()}
        )

    if ayah_order < 6236:
        buttons.append(
            {"text": "➡️", "cd": ChooseAyah(ayah_order=ayah_order + 1).pack()}
        )

    return _build_kb(buttons, back=PagingCB(start=surah, kb_for="surah").pack())
