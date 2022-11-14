
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from telegram.update import Update
import logging  



logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.DEBUG)


updater = Updater(token='5654862420:AAEK0j4WzOWXLwFNGoPGH1WP_yLS4RK1gHs')

dispatcher: Dispatcher = updater.dispatcher

def generate_keyboard(game: list):
    NONE = "⏹"
    CROSS = "❌"
    CIRCLE = "⭕️"

    keyboard = []

    for i in range(3):
        temprory_keyboard = []
        for j in range(3):
            index = i*3+j 
            item = game[index]
            if item == 0:
                temprory_keyboard.append(InlineKeyboardButton(text=NONE, callback_data=index))
            elif item == 1:
                temprory_keyboard.append(InlineKeyboardButton(text=CROSS, callback_data=index))
            elif item == 2:
                temprory_keyboard.append(InlineKeyboardButton(text=CIRCLE, callback_data=index))
        keyboard.append(temprory_keyboard)
    return keyboard


def inline_query(update: Update, context: CallbackContext):
    query = update.inline_query.query
    keyboard = generate_keyboard([0,0,0,0,0,0,0,0,0])
    update.inline_query.answer([
        InlineQueryResultArticle(
            id="x", title="X", 
            input_message_content = InputTextMessageContent('X'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
        InlineQueryResultArticle(
            id="o", title="O", 
            input_message_content = InputTextMessageContent('O'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
    ])

def callback_query(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    index = int(query.data)

    game = [0,0,0,0,0,0,0,0,0] 
    game[index] = 1

    query.edit_message_text(
        text=f"selected option", 
        reply_markup=InlineKeyboardMarkup(generate_keyboard(game)))



dispatcher.add_handler(InlineQueryHandler(inline_query))
dispatcher.add_handler(CallbackQueryHandler(callback_query))

updater.start_polling()
updater.idle()