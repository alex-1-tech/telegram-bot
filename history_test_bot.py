from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import datetime
import random
import sys
import json

test = {
    'score': 0,
    'question':
        {
            'test':
                [
                    {
                        'question': 'test',
                        'response': 'test'
                    }
                ]
        },
    'iter': 0
}


def start(update, context):
    update.message.reply_text(
        'Введите /go , если вы желаете пройти опрос!'
    )
    test['score'] = 0
    with open('history_test.json', encoding='utf-8') as f:
        a = json.load(f)
        random.shuffle(a['test'])
        test['question'] = a
    return 1

def response(update, context):
    if test['iter'] != 0:
        if update.message.text == test['question']['test'][test['iter'] - 1]['response']:
            test['score'] += 1
    if test['iter'] == len(test['question']['test']):
        update.message.reply_text(
            'Ваш счет {} из {}'.format(
                test['score'], len(test['question']['test']
                                   )
            )
        )
        stop(update, context)
        return ConversationHandler.END
    update.message.reply_text(
        test['question']['test'][test['iter']]['question']
    )
    test['iter'] += 1
    return 1


def stop(update, context):
    update.message.reply_text(
        'Спасибо за участие!\nВаш бал: %s' % test['score']
    )


def main():
    updater = Updater('5165907301:AAHJ13f3RmDp6S-tkqoB4flgtLiwGn46veU', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text, response)],
        },
        fallbacks=[CommandHandler('stop', stop)]
    ))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
