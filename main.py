import bot.load_config as load_config
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(
        update.effective_user,
        "----",
        update.effective_chat.id,
        "----",
        update.message.message_id,
    )
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text=f"Hello {update.effective_user.first_name}",
    #     reply_to_message_id=update.message.message_id,
    # )


app = ApplicationBuilder().token(load_config.telegram_bot_token).build()
app.add_handler(CommandHandler("hello", start))

app.run_webhook(listen="0.0.0.0", port=8080, webhook_url=load_config.web_hook_url)
