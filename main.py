from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, \
    InlineQueryHandler, CallbackQueryHandler
from telegram.update import Update
import logging

logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.DEBUG)

updater = Updater(token='5654862420:AAEK0j4WzOWXLwFNGoPGH1WP_yLS4RK1gHs')

dispatcher: Dispatcher = updater.dispatcher


class Game:
    def __init__(self, context: CallbackContext) -> None:
        self._context = context
        self._chat_data = context.chat
        self._chat_data.update({
            'game_increment': 1,
        })
        self.game_name = None
        self.game = None

    def _get_next_game_id(self):
        _id = self._chat_data['game_increment']
        self._chat_data.update({
            'game_increment': _id + 1
        })
        return _id

    def store_data(self):
        self._chat_data.update({
            self.game_name: self.game
        })

    def new_game(self):
        self.game_name = 'game' + str(self._get_next_game_id())
        self.game_name = {
            'player1': None,
            'player2': None,
            'game': [0, 0, 0, 0, 0, 0, 0, 0, 0],
            'turn': False,  # False <- player1 / True <- player2
        }
        self.store_data()

    def get_game(self, name):
        self.game = self._chat_data.get(name, None)


def generate_keyboard(game: Optional[Game]):
    NONE = "⏹"
    CROSS = "❌"
    CIRCLE = "⭕️"

    keyboard = []

    for i in range(3):
        temprory_keyboard = []
        for j in range(3):
            index = i * 3 + j
            if game is None:
                item = 0
                callback_data = f'new_game|{index}'
            else:
                item = game[index]
                callback_data = f'{game.game_name}|{index}'
            # item = game[index]
            text = NONE if item == 0 else CROSS if item == 1 else CIRCLE
            temprory_keyboard.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data))
        keyboard.append(temprory_keyboard)
    return keyboard


def inline_query(update: Update, context: CallbackContext):
    keyboard = generate_keyboard(None)
    update.inline_query.answer([
        InlineQueryResultArticle(
            id="x", title="X",
            input_message_content=InputTextMessageContent('X'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
        InlineQueryResultArticle(
            id="o", title="O",
            input_message_content=InputTextMessageContent('O'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
    ])


def callback_query(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    print(query)

    # index = int(query.data)

    # game = [0,0,0,0,0,0,0,0,0] 
    # game[index] = 1

    # query.edit_message_text(
    #     text=f"selected option", 
    #     reply_markup=InlineKeyboardMarkup(generate_keyboard(game)))


dispatcher.add_handler(InlineQueryHandler(inline_query))
dispatcher.add_handler(CallbackQueryHandler(callback_query))

updater.start_polling()
updater.idle()
