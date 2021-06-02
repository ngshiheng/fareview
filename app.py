import logging
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, Updater

from fareview.models import User, db_connect
from fareview.settings import SUPPORTED_BRANDS, TELEGRAM_API_TOKEN

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
    """
    Start the conversation and ask user for input.
    """
    result = ConversationHandler.END
    update.message.reply_text('Hi! 👋 My name is FareviewBot. 🎉 Welcome aboard!\n')
    user_info = update.message.from_user
    logger.info(f'User with user_info={user_info} just started conversation with the bot.')

    try:
        user = session.query(User).filter_by(telegram_chat_id=user_info.id).one_or_none()
        if not user:
            logger.info('User not found, creating a new user account for user.')
            new_user = User(
                telegram_chat_id=user_info.id,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
                alert_settings=SUPPORTED_BRANDS,
            )
            session.add(new_user)

            update.message.reply_text(
                '🎁 As welcome gift from us, you are given 30 days of free trial!\n'
                '🚨 You will now receive price alerts on a daily basis.\n'
                '👇 Please tap on the \'Email\' option to verify your email address.\n',
                reply_markup=markup,
            )

        else:
            logger.info('User found, check if user has a valid membership.')
            user.last_active_on = datetime.utcnow()
            if user.membership_end_date >= datetime.utcnow():
                time_left = user.membership_end_date - datetime.utcnow()

                update.message.reply_text(
                    '🚨 You will now receive price alerts on a daily basis. \n'
                    f'💡 Do note that your current subscription ends in {time_left.days + 1} days. \n'
                    '👇 To update your email, please tap on the \'Email\' option.\n',
                    reply_markup=markup,
                )

            else:
                update.message.reply_text(
                    '😪 You will stop receiving any price alerts now.\n'
                    '📨 If you would love to continue receiving price alerts, please contact us at infofareview@gmail.com!\n'
                    '👇 To update your email, please tap on the \'Email\' option.\n',
                    reply_markup=markup,
                )

            result = CHOOSING
        session.commit()

    except Exception as error:
        logger.exception(error)
        session.rollback()
        raise

    finally:
        session.close()

    return result


def update_user_info(update: Update, context: CallbackContext) -> int:
    """
    Ask the user for info about the selected predefined choice
    """
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text('Cool! What is your email address?')

    return TYPING_REPLY


def confirm_user_info(update: Update, context: CallbackContext) -> int:
    """
    Store info provided by user and ask for the next category
    """
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice'].lower()
    user_data[category] = text

    email = user_data['email']

    update.message.reply_text(
        f'Got it! Just to confirm, your email address is {email}.\n'
        'You can always tap on \'Email\' to edit again before saving.\n'
        'Tap \'Save\' to confirm.',
        reply_markup=markup,
    )

    return CHOOSING


def save(update: Update, context: CallbackContext) -> int:
    """
    Display the gathered info and end the conversation
    """
    user_info = update.message.from_user
    user_data = context.user_data

    if not bool(user_data):
        update.message.reply_text(
            'You have not made any changes. \n'
            'Type /start to talk to me again. Until next time! ✌',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    else:
        update.message.reply_text(
            'Email saved. 🙏\n'
            'Type /start to talk to me again. Until next time! ✌',
            reply_markup=ReplyKeyboardRemove(),
        )

    try:
        user = session.query(User).filter_by(telegram_chat_id=user_info.id).one_or_none()
        if user:
            # Update user's `telegram_chat_id`
            user.email = user_data['email']
            session.commit()

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
    assert TELEGRAM_API_TOKEN, 'TELEGRAM_API_TOKEN is not configured.'
    updater = Updater(TELEGRAM_API_TOKEN)

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
    updater.start_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path=TELEGRAM_API_TOKEN,
        webhook_url='https://fareview.herokuapp.com/' + TELEGRAM_API_TOKEN,
    )

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully
    updater.idle()


if __name__ == '__main__':
    main()
