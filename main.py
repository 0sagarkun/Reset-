import re
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

BOT_TOKEN = "8958526751:AAFFgAa3X-lYA7jx-5F9SHTv6PZZqPxZeW0"

WAITING_FOR_EMAIL = 1

async def send_reset_link(email: str) -> str:
    headers = {
        "User-Agent": "Instagram 368.0.0.45.96 Android (30/11; 440dpi; 1080x2220; Xiaomi/Redmi; 23127PN0CC; begonia; mt6785; ar_EG; 700073482)",
        "Content-Type": "application/x-www-form-urlencoded",
        "x-bloks-version-id": "dbfb0f84b6481f4ec0a033d7947fb45db546b8cee18dde220c4c1eefd3bb3dcb",
        "x-ig-app-id": "567067343352427",
    }
    data = {
        "search_query": email,
        "bloks_versioning_id": "dbfb0f84b6481f4ec0a033d7947fb45db546b8cee18dde220c4c1eefd3bb3dcb"
    }
    try:
        async with httpx.AsyncClient(http2=True, headers=headers, timeout=20.0) as client:
            response = await client.post(
                "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.caa.ar.search.async/",
                data=data
            )
            if f"We sent a link to {email}. Use that link to confirm your account." in response.text:
                return f"✅ Reset link sent to `{email}`"
            else:
                return f"❌ Email `{email}` not found or invalid."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Reset Instagram Password", callback_data="reset")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome = (
        "👋 *Welcome to Instagram Password Reset Bot*\n\n"
        "Click the button below to reset your Instagram password.\n\n"
        "👨‍💻 *Developer:* @sagarkun0 (sagar)"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "reset":
        await query.edit_message_text(
            "📧 Please send me your Instagram email address.\n\n"
            "Type or paste the email here.\n"
            "Example: `myemail@gmail.com`\n\n"
            "You can also type /cancel to stop.",
            parse_mode="Markdown"
        )
        return WAITING_FOR_EMAIL

    elif query.data == "help":
        help_text = (
            "🔍 *How it works*\n\n"
            "1. Click 'Reset Instagram Password'\n"
            "2. Send your Instagram email\n"
            "3. I will request a password reset link from Instagram\n\n"
            "⚠️ *Note:* This only works if the email is registered on Instagram.\n"
            "The bot does not store any emails.\n\n"
            "📌 Developer: @sagarkun0"
        )
        await query.edit_message_text(help_text, parse_mode="Markdown")
        await show_main_menu(query.message.chat.id, context)
        return ConversationHandler.END

    elif query.data == "about":
        about_text = (
            "🤖 *Instagram Reset Bot*\n"
            "👨‍💻 Created by @sagarkun0 (sagar)\n"
            "⚡ Version 2.0 - Inline buttons only\n"
            "📡 Uses Instagram's official async API\n\n"
            "⚠️ For educational purposes only."
        )
        await query.edit_message_text(about_text, parse_mode="Markdown")
        await show_main_menu(query.message.chat.id, context)
        return ConversationHandler.END

    return ConversationHandler.END

async def show_main_menu(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("🔐 Reset Instagram Password", callback_data="reset")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="*Main Menu:* Choose an option below.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        await update.message.reply_text("❌ Invalid email. Send a real email or /cancel.")
        return WAITING_FOR_EMAIL

    await update.message.reply_text(f"⏳ Trying to send reset link to `{email}`...", parse_mode="Markdown")
    result = await send_reset_link(email)
    await update.message.reply_text(result, parse_mode="Markdown")
    await show_main_menu(update.message.chat_id, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    await show_main_menu(update.message.chat_id, context)
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback, pattern="^reset$")],
        states={WAITING_FOR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)]},
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^(help|about)$"))
    app.add_error_handler(error_handler)
    print("🤖 Bot started by @sagarkun0 (sagar) ...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
