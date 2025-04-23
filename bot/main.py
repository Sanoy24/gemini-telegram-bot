#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from bot import load_config

from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
import re
from bot.core import gemini_client

# from html import escape
import markdown
from md2tgmd import escape

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


import re


def format_for_telegram(text: str) -> str:
    """
    Formats Gemini API response for Telegram with perfect code block and text formatting.
    Handles:
    - Multiline code blocks (```)
    - Inline code (`)
    - Bold text (**)
    - Lists (*)
    - Preserves indentation and spacing
    """
    # Process multiline code blocks first (```code```)
    text = re.sub(
        r"```(\w*)\n(.*?)```",
        lambda m: f"<pre>{m.group(2)}</pre>",
        text,
        flags=re.DOTALL,
    )

    # Process inline code (`code`)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Convert markdown bold (**text**) to HTML bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # Convert markdown lists to bullet points
    text = re.sub(r"^\*\s+(.+)", r"• \1", text, flags=re.MULTILINE)

    # Escape HTML special characters (but preserve our allowed tags)
    text = (
        text.replace("&", "&amp;")
        .replace("<b>", "〖TEMP_B〗")
        .replace("</b>", "〖TEMP_/B〗")
        .replace("<pre>", "〖TEMP_PRE〗")
        .replace("</pre>", "〖TEMP_/PRE〗")
        .replace("<code>", "〖TEMP_CODE〗")
        .replace("</code>", "〖TEMP_/CODE〗")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("〖TEMP_B〗", "<b>")
        .replace("〖TEMP_/B〗", "</b>")
        .replace("〖TEMP_PRE〗", "<pre>")
        .replace("〖TEMP_/PRE〗", "</pre>")
        .replace("〖TEMP_CODE〗", "<code>")
        .replace("〖TEMP_/CODE〗", "</code>")
    )

    # Preserve multiple newlines
    text = text.replace("\n\n", "\n \n")

    return text


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def formatted(text: str) -> str:
    # escaped_text = escape(text)  # Use HTML escaping
    escaped_text = format_for_telegram(text=text)
    return escaped_text


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    data = gemini_client.fetch_gemini_response(text=text)

    formatted_text = escape(data)

    # Send in chunks if needed
    for i in range(0, len(formatted_text), 4096):
        chunk = formatted_text[i : i + 4096]
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=chunk,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"Error sending message: {e}")
            # Fallback to plain text
            await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed

    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("  Prompt  ", callback_data=1),
            InlineKeyboardButton("  Images  ", callback_data=2),
        ],
        [
            InlineKeyboardButton("  ✅ 5 seconds    ", callback_data=1),
            InlineKeyboardButton("  option-2", callback_data=2),
        ],
        [
            InlineKeyboardButton("  ✅ Version 1.6  ", callback_data=1),
            InlineKeyboardButton("  option-2    ", callback_data=2),
        ],
        [
            InlineKeyboardButton("  ✅ 1:1  ", callback_data=1),
            InlineKeyboardButton("  16:9    ", callback_data=2),
            InlineKeyboardButton("  9:16    ", callback_data=2),
        ],
        [InlineKeyboardButton(" ✖️ Cancel Generation    ", callback_data=3)],
        [InlineKeyboardButton(" 🎥 Start Generation", callback_data=3)],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "please choose saadsdsadsad s dsa  dasdsadsadsadsadsad asdsadsadsadsadsa  adasdsadsadsadsdsadasd   dasdsadsadsa:",
        reply_markup=reply_markup,
    )


async def ask(update: Update, contect: ContextTypes.DEFAULT_TYPE):
    pass


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(load_config.telegram_bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("models", model))
    application.add_handler(CallbackQueryHandler(button))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    # application.run_polling(allowed_updates=Update.ALL_TYPES)
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=load_config.web_hook_url,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
