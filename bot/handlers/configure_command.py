from telegram.ext import CommandHandler
from .command import start

start_handler = CommandHandler("start", start)
