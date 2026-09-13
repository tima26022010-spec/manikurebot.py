import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ===== НАСТРОЙКИ =====
BOT_TOKEN = "8715871561:AAHjq0gdaAHG6Yj65Z67GhpCMn3716i7CJQ"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ===== СОСТОЯНИЯ =====
class Quiz(StatesGroup):
    mood = State()
    style = State()
    occasion = State()
    length = State()


# ===== КЛАВИАТУРЫ =====
def kb_mood():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😊 Весёлое", callback_data="mood_весёлое")],
        [InlineKeyboardButton(text="😎 Уверенное", callback_data="mood_уверенное")],
        [InlineKeyboardButton(text="🌙 Меланхоличное", callback_data="mood_меланхоличное")],
        [InlineKeyboardButton(text="💖 Романтичное", callback_data="mood_романтичное")],
        [InlineKeyboardButton(text="⚡ Энергичное", callback_data="mood_энергичное")],
    ])


def kb_style():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Минимализм", callback_data="style_минимализм")],
        [InlineKeyboardButton(text="🌸 Нежность и мягкость", callback_data="style_нежность")],
        [InlineKeyboardButton(text="🖤 Гранж / тёмная эстетика", callback_data="style_гранж")],
        [InlineKeyboardButton(text="🌈 Яркость и креатив", callback_data="style_яркость")],
        [InlineKeyboardButton(text="🎀 Классика / элегантность", callback_data="style_классика")],
    ])


def kb_occasion():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 На учёбу в колледж", callback_data="occ_учёба")],
        [InlineKeyboardButton(text="🎉 Вечеринка с друзьями", callback_data="occ_вечеринка")],
        [InlineKeyboardButton(text="☕ Прогулка / свидание", callback_data="occ_прогулка")],
        [InlineKeyboardButton(text="📸 Для фото / соцсетей", callback_data="occ_фото")],
        [InlineKeyboardButton(text="🏠 Просто для себя", callback_data="occ_себя")],
    ])


def kb_length():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪶 Очень короткие", callback_data="len_короткие")],
        [InlineKeyboardButton(text="💅 Средние", callback_data="len_средние")],
        [InlineKeyboardButton(text="💎 Длинные", callback_data="len_длинные")],
        [InlineKeyboardButton(text="🎨 Микс (разные)", callback_data="len_микс")],
    ])


def kb_restart():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Пройти заново", callback_data="restart")],
    ])


# ===== ЛОГИКА ПОДБОРА =====
def pick_design(mood: str, style: str, occasion: str, length: str) -> str:
    """Подбирает цвет и дизайн маникюра на основе ответов."""

    # Цвет по настроению
    colors_by_mood = {
        "весёлое":       "яркий коралловый, фуксия или солнечно-жёлтый ☀️",
        "уверенное":     "глубокий чёрный, бордовый или тёмно-синий 🖤",
        "меланхоличное": "пыльно-серый, лавандовый или туманно-голубой 🌫️",
        "романтичное":   "нежно-розовый, пудровый или персиковый 🌸",
        "энергичное":    "неоновый лайм, электрик или оранжевый ⚡",
    }

    # Дизайн по стилю
    design_by_style = {
        "минимализм": (
            "тонкая линия по центру ногтя, одна маленькая точка у кутикулы "
            "или акцент на один ноготь контрастным лаком ✨"
        ),
        "нежность": (
            "полупрозрачная вуаль, лёгкие мраморные разводы, "
            "мини-цветочки или жемчужная пудра 🌸"
        ),
        "гранж": (
            "матовое покрытие, потёртый металлик, чёрные абстрактные линии, "
            "капли и разводы 🖤"
        ),
        "яркость": (
            "градиент, геометрические фигуры разных цветов, "
            "наклейки, стразы и глиттер 🌈"
        ),
        "классика": (
            "френч с тонкой линией, лунный маникюр, "
            "однотонное глянцевое покрытие + блеск на безымянном 🎀"
        ),
    }

    # Акцент по случаю
    occasion_tips = {
        "учёба":     "Держи маникюр аккуратным и не слишком длинным — так удобнее писать конспекты и работать за ноутбуком 📓",
        "вечеринка": "Добавь стразы, глиттер или светящийся лак — на фото и в темноте будет смотреться ярко 🎉",
        "прогулка":  "Пастельные оттенки и лёгкий блеск — идеально для кофе и фото с подругой ☕",
        "фото":      "Смело экспериментируй: акцентные ногти и контрастные узоры отлично смотрятся в кадре 📸",
        "себя":      "Выбирай то, что поднимает настроение лично тебе — никаких правил 💗",
    }

    # Форма/длина
    length_tips = {
        "короткие": "Короткая длина = аккуратно и практично. Отлично смотрятся минимализм и тонкие линии.",
        "средние":  "Средняя длина универсальна — подойдёт любой дизайн.",
        "длинные":  "На длинных ногтях круто смотрятся градиент, мрамор и крупные акценты.",
        "микс":     "Микс длины — тренд! Например, акцентные длинные ногти + короткие остальные.",
    }

    color = colors_by_mood.get(mood, "нейтральный нюд")
    design = design_by_style.get(style, "однотонное покрытие с блеском")
    occ = occasion_tips.get(occasion, "")
    ln = length_tips.get(length, "")

    return (
        f"💅 <b>Твой идеальный маникюр</b>\n\n"
        f"🎨 <b>Цвет:</b> {color}\n\n"
        f"✨ <b>Дизайн:</b> {design}\n\n"
        f"📌 <b>Совет по случаю:</b> {occ}\n\n"
        f"💡 <b>Про длину:</b> {ln}\n\n"
        f"Удачи в колледже и пусть ногти радуют! 💖"
    )


# ===== ХЕНДЛЕРЫ =====
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Специально для лусипосика\n\n"
        "Вот тута короче пару вопросов\n"
        "Я не знаю как это будет работать.\n\n"
        "<b>Вопрос 1/4: Какое у тебя сейчас настроение?</b>",
        reply_markup=kb_mood(),
        parse_mode="HTML",
    )
    await state.set_state(Quiz.mood)


@dp.callback_query(Quiz.mood, F.data.startswith("mood_"))
async def answer_mood(call: CallbackQuery, state: FSMContext):
    await state.update_data(mood=call.data.split("_", 1)[1])
    await call.message.edit_text(
        "<b>Вопрос 2/4: Какой стиль тебе ближе?</b>",
        reply_markup=kb_style(),
        parse_mode="HTML",
    )
    await state.set_state(Quiz.style)
    await call.answer()


@dp.callback_query(Quiz.style, F.data.startswith("style_"))
async def answer_style(call: CallbackQuery, state: FSMContext):
    await state.update_data(style=call.data.split("_", 1)[1])
    await call.message.edit_text(
        "<b>Вопрос 3/4: Для какого случая нужен маникюр?</b>",
        reply_markup=kb_occasion(),
        parse_mode="HTML",
    )
    await state.set_state(Quiz.occasion)
    await call.answer()


@dp.callback_query(Quiz.occasion, F.data.startswith("occ_"))
async def answer_occasion(call: CallbackQuery, state: FSMContext):
    await state.update_data(occasion=call.data.split("_", 1)[1])
    await call.message.edit_text(
        "<b>Вопрос 4/4: Какую длину ногтей предпочитаешь?</b>",
        reply_markup=kb_length(),
        parse_mode="HTML",
    )
    await state.set_state(Quiz.length)
    await call.answer()


@dp.callback_query(Quiz.length, F.data.startswith("len_"))
async def answer_length(call: CallbackQuery, state: FSMContext):
    await state.update_data(length=call.data.split("_", 1)[1])
    data = await state.get_data()

    result = pick_design(
        data["mood"], data["style"], data["occasion"], data["length"]
    )

    await call.message.edit_text(
        result,
        reply_markup=kb_restart(),
        parse_mode="HTML",
    )
    await state.clear()
    await call.answer("Готово! ✨")


@dp.callback_query(F.data == "restart")
async def restart(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "Начнём заново! 💫\n\n<b>Вопрос 1/4: Какое у тебя сейчас настроение?</b>",
        reply_markup=kb_mood(),
        parse_mode="HTML",
    )
    await state.set_state(Quiz.mood)
    await call.answer()


# ===== ЗАПУСК =====
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())