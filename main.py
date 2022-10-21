
from telegram import InlineQueryResultArticle
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, InlineQueryHandler
from telegram.update import Update
import requests  


updater = Updater(token='5654862420:AAEK0j4WzOWXLwFNGoPGH1WP_yLS4RK1gHs')



dispatcher: Dispatcher = updater.dispatcher

def inline_query(update: Update, context: CallbackContext):
    query = update


dispatcher.add_handler(InlineQueryHandler(inline_query))

updater.start_polling()
updater.idle()