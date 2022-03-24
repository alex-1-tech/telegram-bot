from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import random

REQUEST_KWARGS = {
    'proxy_url': 'socks5://ip:port',
}
STATE = 0


def create_start_keyboard(update, text):
    reply_keyboard = [['/dice', '/timer'], ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        text,
        reply_markup=markup,
    )


def start(update, context):
    global STATE
    STATE = 0
    # keyboard
    create_start_keyboard(update,
                          'Приветствую! Я твой личный Бот!\n'
                          'Какая вам нужна информация?')


def close_keyboard(update, context):
    update.message.reply_text(
        "OK",
        reply_markup=ReplyKeyboardRemove(),
    )


def help(update, context):
    update.message.reply_text(
        "Я беспомощный :("
    )


def create_dicer(update, context):
    global STATE
    STATE = 2
    # keyboard
    reply_keyboard = [
        [
            'кинуть один шестигранный кубик',
            'кинуть 2 шестигранных кубика одновременно',
        ],
        [
            'кинуть 20-гранный кубик',
            'вернуться назад',
        ],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    update.message.reply_text(
        'Принял!',
        reply_markup=markup,
    )


# timer_settings
def create_timer(update, context):
    global STATE
    STATE = 1
    # keyboard
    reply_keyboard = [
        [
            '30 секунд',
            '1 минута',
        ],
        [
            '5 минут',
            'вернуться назад',
        ],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    update.message.reply_text(
        'Принял!',
        reply_markup=markup,
    )


def task(context):
    job = context.job
    context.bot.send_message(job.context, text='Время истекло')


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def unset_timer(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Хорошо, вернулся сейчас!' if job_removed else 'Нет активного таймера.'
    update.message.reply_text(text)


def set_timer(update, context, due=None):
    chat_id = update.message.chat_id
    try:
        if due is None:
            due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, мы не умеет возвращаться в прошлое'
            )
            return
        job_removed = remove_job_if_exists(
            str(chat_id),
            context
        )

        context.job_queue.run_once(
            task,
            due,
            context=chat_id,
            name=str(chat_id),
        )

        text = f'Засек {due} секунд.'
        if job_removed:
            text += ' Старая задача удалена.'
        update.message.reply_text(
            text
        )
    except (IndexError, ValueError):
        update.message.reply_text("Использование: /set <секунд>")


# end timer settings

def tasks(update, context):
    global STATE
    if update.message.text == 'вернуться назад':
        update.message.reply_text(
            'OK',
            reply_markup=ReplyKeyboardRemove(),
        )
        create_start_keyboard(update, 'Что желаете сделать?')
    elif STATE == 2:
        # dice
        if update.message.text == 'кинуть один шестигранный кубик':
            update.message.reply_text(
                'Вам выпал кубик с номером: ' + str(random.randint(1, 6))
            )
        elif update.message.text == 'кинуть 2 шестигранных кубика одновременно':
            update.message.reply_text(
                f'Вам ввыпали кубики с номерами: {random.randint(1, 6)}'
                f' и {random.randint(1, 6)}'
            )
        elif update.message.text == 'кинуть 20-гранный кубик':
            update.message.reply_text(
                'Вам выпал кубик с номером: ' + str(random.randint(1, 20))
            )
    elif STATE == 1:
        if update.message.text == '30 секунд':
            set_timer(update, context, 30)
        elif update.message.text == '1 минута':
            set_timer(update, context, 60)
        elif update.message.text == '5 минут':
            set_timer(update, context, 300)


def main():
    # create object upedater
    updater = Updater('5165907301:AAHJ13f3RmDp6S-tkqoB4flgtLiwGn46veU', use_context=True)
    # take from updater message manager
    dp = updater.dispatcher

    # command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler('timer', create_timer))
    dp.add_handler(CommandHandler('dice', create_dicer))
    # command timer handler
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset_timer,
                                  pass_chat_data=True))

    # message handlers
    dp.add_handler(MessageHandler(Filters.text, tasks))
    # start bot
    updater.start_polling()

    # waiting for the end of the application
    # signal SIG_TERM ( Ctrl + C )
    updater.idle()


if __name__ == '__main__':
    main()
