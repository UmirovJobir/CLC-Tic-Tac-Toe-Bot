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
        self._bot_data = context.bot_data
        self._bot_data.update({
            'game_increment': 1,
        })
        self.game_name = None
        self.game = None

    def _get_next_game_id(self):
        _id = self._bot_data['game_increment']
        self._bot_data.update({
            'game_increment': _id + 1
        })
        return _id

    def store_data(self):
        self._bot_data.update({
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
        self.game = self._bot_data.get(name, None)


    def make_move(self, user: User, index: int):
        game = self.game
        player1 = game['player1']
        player2 = game['player2']
        is_player1_first = self.game['is_player1_first']

        if player2['id'] is None:
            if user.id != player1['id']:
                self.set_player2(user)
                player2 = game['player2']
            else:
                return

        if not (player1['id'] == user.id or
                player2['id'] == user.id):
            return

        turn = game['turn']

        if index is None:
            return

        current_player = player2 if turn else player


def generate_keyboard(game: Optional[Game]):
    NONE = "⏹"
    CROSS = "❌"
    CIRCLE = "⭕"

    keyboard = []

    for i in range(3):
        temprory_keyboard = []
        for j in range(3):
            index = i * 3 + j
            if game is None:
                item = 0
                callback_data = f'new_game'
            else:
                item = game.game['game'][index]
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

    game = Game(context)
    is_player1_first = True
    index = None

    if 'new_game' in query.data:
        is_player1_first = \
            True if query.data.split('|')[1] == 'True' else False
        game.new_game(is_player1_first=is_player1_first)
        game.set_player1(update.effective_user)
    else:
        game_name, index = query.data.split('|')
        index = int(index)
        game.get_game(game_name)
        if game.game is None:
            game.new_game(is_player1_first=is_player1_first)
            game.set_player1(update.effective_user)

    game.make_move(update.effective_user, index)

    print(game.game)

    query.edit_message_text(
        text=f"selected option",
        reply_markup=InlineKeyboardMarkup(generate_keyboard(game)))

    print(query)

    # index = int(query.data)
    #
    # game = [0,0,0,0,0,0,0,0,0]
    # game[index] = 1
    #


dispatcher.add_handler(InlineQueryHandler(inline_query))
dispatcher.add_handler(CallbackQueryHandler(callback_query))

updater.start_polling()
updater.idle()
