from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, \
    InlineQueryHandler, CallbackQueryHandler, DictPersistence
from telegram.update import Update
import logging
import settings

logging.basicConfig(
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    level=logging.DEBUG)
persistence = DictPersistence()
updater = Updater(
    token=settings.TOKEN,
    persistence=persistence
    )

dispatcher: Dispatcher = updater.dispatcher

NONE = '⬜'
CROSS = '❌'
CIRCLE = '⭕'
HAND = '👈'
WINNER = '🤩'
LOSER = '😭'
DRAW = '😡'

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
        temp = self.game.copy()
        temp.update({
            'grid': self.game['grid'].items
        })
        self._bot_data.update({
            self.game_name: temp
        })

    def new_game(self):
        self.game_name = 'game' + str(self._get_next_game_id())
        self.game_name = {
            'player1': {
                'id': None,
                'name': '?'
            },
            'player2': {
                'id': None,
                'name': '?'
            },
            'grid': Grid([]),
            # False <- player1
            # True <- player2
            'turn': False,
            # True <- player1 = x, player2 = o
            # False <- player1 = o, player2 = x
            'is_player1_first': is_player1_first,
        }
        self.store_data()

    def get_turn_message(self):
        game = self.game
        player1 = game['player1']
        player2 = game['player2']
        turn = game['turn']
        is_player_first = game['is_player1_first']

        return f"{CROSS if is_player_first else CIRCLE}" \
               f"{player1['name']}" \
               f"{'' if turn else HAND}" \
               f"\n" \
               f"{CIRCLE if is_player_first else CROSS}" \
               f"{player2['name']}" \
               f"{HAND if turn else ''}"


    def get_game(self, name):
        self.game_name = name
        self.game = self._bot_data.get(name, None)
        if self.game is not None:
            temp = self.game.get('grid')
            grid = Grid([])
            if temp is list:
                grid = Grid(temp)
            self.game.update({
                'grid': grid
            })

    def get_end_message(self):
        game = self.game
        player1 = game['player1']
        player2 = game['player2']
        is_player_first = game['is_player1_first']
        grid: Grid = self.game['grid']
        winner = grid.get_winner()
        player1_emoji = DRAW
        player2_emoji = DRAW

        if winner:
            if is_player_first:
                player1_emoji = WINNER if winner == 1 else LOSER
                player2_emoji = WINNER if winner == 2 else LOSER
            else:
                player1_emoji = LOSER if winner == 1 else WINNER
                player2_emoji = LOSER if winner == 2 else WINNER

        return f"{CROSS if is_player_first else CIRCLE}" \
               f" {player1['name']} " \
               f"{player1_emoji}" \
               f"\n" \
               f"{CIRCLE if is_player_first else CROSS}" \
               f" {player2['name']} " \
               f"{player2_emoji}"

    def switch_turn(self):
        turn = self.game['turn']
        self.game['turn'] = not turn
        self.store_data()

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

        current_player = player2 if turn else player1

        if current_player['id'] != user.id:
            return

        grid = game['grid']

        can_turn = grid.items[index] == 0

        if not can_turn:
            return

        grid.items[index] = 1 if is_player1_first and not turn else 2

        self.store_data()

        self.switch_turn()


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
