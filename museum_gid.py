from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import random
import sys


def bye(update, context):
    update.message.reply_text('Всего доброго, не забудьте забрать верхнюю одежду в гардеробе!')


def actions(name):
    scene = {
        '1': ['2', 'Выход'],
        '2': ['3'],
        '3': ['1', '4'],
        '4': ['1'],
    }
    if name not in scene:
        print('Неправильная комната')
        sys.exit(0)
    text = 'Добро пожаловать!\nПожалуйста, сдайте верхнюю одежду в гардероб!\n'
    text += f'Вы в комнате номер {name}.\nВозможные варианты действий: '
    for i in scene[name]:
        text += '\n    Перейти в комнату: ' + i
    return text


def start(update, context):
    update.message.reply_text(actions('1'))
    return 1


def first(update, context):
    if update.message.text == '2':
        bye(update, context)
        update.message.reply_text(actions('2'))
        return 2
    elif update.message.text == 'Выход':
        return end(update, context)
    else:
        update.message.reply_text('Нельзя перейти в такую комнату!')
    return 1


def second(update, context):
    if update.message.text == '3':
        bye(update, context)
        update.message.reply_text(actions('3'))
        return 3
    else:
        update.message.reply_text('Нельзя перейти в такую комнату!')
    return 2


def third(update, context):
    if update.message.text == '1':
        bye(update, context)
        update.message.reply_text(actions('1'))
        return 1
    elif update.message.text == '4':
        bye(update, context)
        update.message.reply_text(actions('4'))
        return 4
    else:
        update.message.reply_text('Нельзя перейти в такую комнату!')
    return 3


def fourth(update, context):
    if update.message.text == '1':
        bye(update, context)
        update.message.reply_text(actions('1'))
        return 1
    else:
        update.message.reply_text('Нельзя перейти в такую комнату!')
    return 3


def end(update, context):
    bye(update, context)
    update.message.reply_text('Спасибо, что посетили нас! Приходите еще!')
    return ConversationHandler.END


def main():
    updater = Updater('5165907301:AAHJ13f3RmDp6S-tkqoB4flgtLiwGn46veU', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text, first)],
            2: [MessageHandler(Filters.text, second)],
            3: [MessageHandler(Filters.text, third)],
            4: [MessageHandler(Filters.text, fourth)],
        },
        fallbacks=[CommandHandler('end', end)]
    ))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
