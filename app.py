import logging
import os
from typing import Dict

from sqlalchemy.orm import sessionmaker
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

from fareview.models import User, db_connect

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

engine = db_connect()
session = sessionmaker(bind=engine)()

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['Email'],
    ['Save'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, _: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text('Hi! 👋 My name is FareviewBot. Welcome aboard!')

    user_info = update.message.from_user
    logger.info(f'User with user_info="{user_info}" started conversation with the bot.')

    user = session.query(User).filter_by(telegram_chat_id=user_info.id).one_or_none()
    session.close()

    if not user:
        update.message.reply_text(
            'Please provide us your registered email address for verification.\n\n'
            'You will start receiving price alerts if you are a verified customer.',
            reply_markup=markup,
        )
        return CHOOSING

    update.message.reply_text(
        'Welcome back! As an existing customer, will now receive price alerts.'
    )
    return ConversationHandler.END


def user_update(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text('What is your email address?')

    return TYPING_REPLY


def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        'Neat! Just so you know, this is what you told me:'
        f'{facts_to_str(user_data)}\n\n'
        'You can always update your information.',
        reply_markup=markup,
    )

    return CHOOSING


def save(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    if not bool(user_data):
        update.message.reply_text(
            'You have not made any changes. Until next time!',
            reply_markup=ReplyKeyboardRemove(),
        )

    else:
        update.message.reply_text(
            f"Here are your most recent saved settings: {facts_to_str(user_data)}"
            "Talk to you soon!",
            reply_markup=ReplyKeyboardRemove(),
        )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.environ.get('TELEGRAM_API_TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Email|Phone Number)$'),
                    user_update
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Save$')),
                    user_update
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Save$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Save$'), save)],
    )

    dispatcher.add_handler(conversation_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
