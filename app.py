import logging
import os
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

from fareview.models import User, db_connect
from fareview.utils.bot import facts_to_str

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


def start(update: Update, _: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    result = ConversationHandler.END
    update.message.reply_text('Hi! 👋 My name is FareviewBot. Welcome aboard! 🎉')
    user_info = update.message.from_user
    logger.info(f'User with user_info <{user_info}> just started conversation with the bot.')

    try:
        user = session.query(User).filter_by(telegram_chat_id=user_info.id).one_or_none()
        if not user:
            new_user = User(
                telegram_chat_id=user_info.id,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )
            session.add(new_user)

        else:
            user.last_active_on = datetime.utcnow()

        session.commit()

        if user and user.email and user.membership_start_date and user.membership_start_date and datetime.utcnow() <= user.membership_end_date:
            update.message.reply_text(
                'As an existing customer, you will now receive price alerts. 🚨\n'
            )

        else:
            update.message.reply_text(
                'Please select the \'Email\' option to update your email address for verification. ✅\n'
                'You will start receiving price alerts if you are a verified customer. 🚨\n'
                'Type /start to update your account information. ⚙️',
                reply_markup=markup,
            )
            result = CHOOSING

    except Exception as error:
        logger.exception(error)
        session.rollback()
        raise

    finally:
        session.close()

    return result


def update_user_info(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text('Cool! What is your email address?')

    return TYPING_REPLY


def confirm_user_info(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice'].lower()
    user_data[category] = text

    update.message.reply_text(
        'Awesome! Just so you know, this is what you told me:'
        f'{facts_to_str(user_data)}'
        'You can always edit again before saving.'
        'Do remember to click \'Save\' before leaving.',
        reply_markup=markup,
    )

    return CHOOSING


def save(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_info = update.message.from_user
    user_data = context.user_data

    if not bool(user_data):
        update.message.reply_text(
            'You have not made any changes. Until next time!\n'
            'Type /start to update your information.',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    else:
        update.message.reply_text(
            f'Here are your most recent saved settings: {facts_to_str(user_data)}'
            'Talk to you soon!',
            reply_markup=ReplyKeyboardRemove(),
        )

    try:
        user = session.query(User).filter_by(email=user_data['email']).one_or_none()
        if user:
            # Update user's `telegram_chat_id`
            user.telegram_chat_id = user_info.id
            session.commit()

        else:
            update.message.reply_text(
                'My apologies, we could not find any information about your account.\n'
                'Please contact inforfareview@gmail.com for help.'
            )

    except Exception as error:
        logger.exception(error)
        raise

    finally:
        session.close()
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
                    Filters.regex('^(Email)$'),
                    update_user_info
                ),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Save$')),
                    update_user_info
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Save$')),
                    confirm_user_info,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Save$'), save)],
    )

    dispatcher.add_handler(conversation_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
