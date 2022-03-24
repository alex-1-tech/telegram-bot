from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import random

REQUEST_KWARGS = {
    'proxy_url': 'socks5://ip:port',
}


class GameBot:
    def __init__(self):
        self.STATE = 0

    def game_bot_start(self, update, context):
        self.STATE = 0
        # keyboard
        self.create_start_keyboard(update,
                                   'Я твой личный Игровой Бот!\n'
                                   'Какая вам нужна информация?')

    def create_start_keyboard(self, update, text):
        reply_keyboard = [['/dice', '/timer'], ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text(
            text,
            reply_markup=markup,
        )

    def close_keyboard(self, update, context):
        update.message.reply_text(
            "OK",
            reply_markup=ReplyKeyboardRemove(),
        )

    def help(self, update, context):
        update.message.reply_text(
            "Я беспомощный :("
        )

    def create_dicer(self, update, context):
        self.STATE = 2
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
    def create_timer(self, update, context):
        self.STATE = 1
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

    def task(self, context):
        job = context.job
        context.bot.send_message(job.context, text='Время истекло')

    def remove_job_if_exists(self, name, context):
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    def unset_timer(self, update, context):
        chat_id = update.message.chat_id
        job_removed = self.remove_job_if_exists(str(chat_id), context)
        text = 'Хорошо, вернулся сейчас!' if job_removed else 'Нет активного таймера.'
        update.message.reply_text(text)

    def set_timer(self, update, context, due=None):
        chat_id = update.message.chat_id
        try:
            if due is None:
                # args[0] - value arg ( seconds )
                due = int(context.args[0])
            if due < 0:
                update.message.reply_text(
                    'Извините, мы не умеет возвращаться в прошлое'
                )
                return
            job_removed = self.remove_job_if_exists(
                str(chat_id),
                context
            )

            context.job_queue.run_once(
                self.task,
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

    def tasks(self, update, context):
        if update.message.text == 'вернуться назад':
            update.message.reply_text(
                'OK',
                reply_markup=ReplyKeyboardRemove(),
            )
            self.create_start_keyboard(update, 'Что желаете сделать?')
        elif self.STATE == 2:
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
        elif self.STATE == 1:
            if update.message.text == '30 секунд':
                self.set_timer(update, context, 30)
            elif update.message.text == '1 минута':
                self.set_timer(update, context, 60)
            elif update.message.text == '5 минут':
                self.set_timer(update, context, 300)


def start(update, context):
    # keyboard
    reply_keyboard = [['/game_bot', '/other_bot'], ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        'Приветствую! Я твой личный Бот!\n'
        'Какой бот вам нужен?',
        reply_markup=markup,
    )


def main():
    # create object upedater
    updater = Updater('5165907301:AAHJ13f3RmDp6S-tkqoB4flgtLiwGn46veU', use_context=True)
    # take from updater message manager
    dp = updater.dispatcher

    # game bot
    game_bot = GameBot()
    # command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("game_bot", game_bot.game_bot_start))
    dp.add_handler(CommandHandler("help", game_bot.help))
    dp.add_handler(CommandHandler("close", game_bot.close_keyboard))
    dp.add_handler(CommandHandler('timer', game_bot.create_timer))
    dp.add_handler(CommandHandler('dice', game_bot.create_dicer))
    # command timer handler
    dp.add_handler(CommandHandler("set", game_bot.set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", game_bot.unset_timer,
                                  pass_chat_data=True))

    # message handlers
    dp.add_handler(MessageHandler(Filters.text, game_bot.tasks))
    # start bot
    updater.start_polling()

    # waiting for the end of the application
    # signal SIG_TERM ( Ctrl + C )
    updater.idle()


if __name__ == '__main__':
    main()
