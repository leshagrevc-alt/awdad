import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

# --- КОНСТАНТЫ ---
# Берем токен из переменных окружения Vercel
TOKEN = os.getenv("BOT_TOKEN")

WEBAPP_URL = "https://llxickvpn.vercel.app/"
SUB_LINK = "https://llxickvpn.vercel.app/api/index"
CHANNEL_ID = "@LLxickVPN"
SUPPORT_USER = "LLxick2"
DONATE_URL = "https://yoomoney.ru/to/4100119272702525"

# Ссылки на приложения
URL_V2RAY_ANDROID = "https://play.google.com/store/apps/details?id=com.v2raytun.android"
URL_V2RAY_IOS = "https://apps.apple.com/us/app/v2raytun/id6476628951"
URL_HAPP_ANDROID = "https://play.google.com/store/apps/details?id=com.happproxy&hl=ru"
URL_HAPP_IOS = "https://apps.apple.com/us/app/happ-proxy-utility/id6504287215"

logging.basicConfig(level=logging.INFO)

# Проверка, что токен вообще загрузился
if not TOKEN:
    exit("Error: BOT_TOKEN variable not found in environment!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ПРОВЕРКА ПОДПИСКИ ---
async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        return False

# --- КЛАВИАТУРЫ ---
def get_start_keyboard(is_subscribed: bool):
    builder = InlineKeyboardBuilder()
    if is_subscribed:
        builder.row(InlineKeyboardButton(text="✨ Настроить через Web App", web_app=WebAppInfo(url=WEBAPP_URL)))
        builder.row(InlineKeyboardButton(text="🤖 Настроить через бота", callback_data="step_1_os"))
        builder.row(
            InlineKeyboardButton(text="❤️ Поддержать автора", url=DONATE_URL),
            InlineKeyboardButton(text="🆘 Помощь", url=f"https://t.me/{SUPPORT_USER}")
        )
    else:
        builder.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"))
        builder.row(InlineKeyboardButton(text="🔄 Проверить подписку", callback_data="check_sub"))
    return builder.as_markup()

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        text = (f"👋 **Привет, {message.from_user.first_name}!**\n\n"
                "Как тебе будет удобнее настроить VPN?")
    else:
        text = "🛑 **Доступ ограничен!**\n\nПодпишитесь на наш канал для доступа к VPN."
    
    await message.answer(text, reply_markup=get_start_keyboard(is_subscribed), parse_mode="Markdown")

@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)
    if is_subscribed:
        await callback.answer("✅ Подписка подтверждена!")
        text = (f"👋 **Привет, {callback.from_user.first_name}!**\n\n"
                "Спасибо за подписку! Теперь тебе доступны все функции.\n"
                "Как тебе будет удобнее настроить подключение?")
        await callback.message.edit_text(text, reply_markup=get_start_keyboard(True), parse_mode="Markdown")
    else:
        await callback.answer("❌ Вы всё еще не подписаны на канал!", show_alert=True)

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)
    text = ("🌍 **Главное меню**\n\nВыберите способ настройки:" if is_subscribed 
            else "🛑 **Доступ ограничен!**\n\nПодпишитесь на наш канал.")
    await callback.message.edit_text(text, reply_markup=get_start_keyboard(is_subscribed), parse_mode="Markdown")

# --- ЛОГИКА ШАГОВ ЧЕРЕЗ БОТА ---
@dp.callback_query(F.data == "step_1_os")
async def step_1(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🤖 Android", callback_data="app_android"),
                InlineKeyboardButton(text="🍎 iPhone (iOS)", callback_data="app_ios"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start"))
    await callback.message.edit_text("📍 **Шаг 1:** Ваша платформа:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data.in_(["app_android", "app_ios"]))
async def step_2(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    v2_url = URL_V2RAY_ANDROID if callback.data == "app_android" else URL_V2RAY_IOS
    hp_url = URL_HAPP_ANDROID if callback.data == "app_android" else URL_HAPP_IOS
    builder.row(InlineKeyboardButton(text="📥 V2RayTun", url=v2_url),
                InlineKeyboardButton(text="📥 HAPP", url=hp_url))
    builder.row(InlineKeyboardButton(text="➡️ Дальше", callback_data="step_3_final"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="step_1_os"))
    await callback.message.edit_text("📍 **Шаг 2:** Установите приложение:", reply_markup=builder.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "step_3_final")
async def step_3(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_start"))
    text = (
        "📍 **Шаг 3: Подключение**\n\n"
        "Твоя персональная ссылка (нажми, чтобы скопировать):\n"
        f"`{SUB_LINK}`\n\n"
        "**Инструкция:**\n"
        "1. Открой приложение.\n"
        "2. Нажми '+' и 'Import from Clipboard'.\n"
        "3. Подключайся!"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())