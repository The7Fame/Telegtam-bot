from help_commands import lowprice_highprice_bestdeal
from db.users import User
from loader import bot
from db import model
from datetime import datetime


@bot.message_handler(commands=['start'])
def start(message):
    """Функция, выводит приветственное сообщение, при открытии телеграм-бота
    :param message:
    :return: None
    """
    bot.send_message(message.chat.id, f"Добрый день, {message.from_user.first_name}!"
                                      "\nЯ помогу вам подобрать отель. "
                                      "\n Нажмите на /help либо напишите, чтобы узнать существующие команды")


@bot.message_handler(commands=['lowprice'])
def lowprice_command(message):
    """Функция /lowprice, выводит список самых дешевых отелей
    :param message:
    :return: None
    """
    user = User.get_user(message.from_user.id)
    user.command = 'дешёвые отели'
    user.time_of_use = datetime.today().strftime('%d.%m.%Y %H:%M:%S')
    lowprice_highprice_bestdeal.low_high_best_func(message)


@bot.message_handler(commands=['highprice'])
def highprice_command(message):
    """Функция выводит список самых дорогих отелей
    :param message:
    :return: None
    """
    user = User.get_user(message.from_user.id)
    user.command = 'дорогие отели'
    user.time_of_use = datetime.today().strftime('%d.%m.%Y %H:%M:%S')
    lowprice_highprice_bestdeal.low_high_best_func(message)


@bot.message_handler(commands=['bestdeal'])
def bestdeal_command(message):
    """Функция выводит список отелей,
    наиболее подходящих по цене и расположению
    :param message:
    :return: None
    """
    user = User.get_user(message.from_user.id)
    user.command = 'Ваш запрос на отель'
    user.time_of_use = datetime.today().strftime('%d.%m.%Y %H:%M:%S')
    lowprice_highprice_bestdeal.low_high_best_func(message)


@bot.message_handler(commands=['history'])
def history_command(message):
    """Функция выводит историю запросов пользователя
    :param message:
    :return: None
    """
    model.req_history(message)


@bot.message_handler(commands=['help'])
def help_command(message):
    """Функция выводит список доступных команд телеграм-бота
    :param message:
    :return: None
    """
    bot.send_message(message.from_user.id, '/lowprice — дешёвые отели\n'
                                           '/highprice — дорогие отели\n'
                                           '/bestdeal — Ваш запрос на отель\n'
                                           '/history — история')


@bot.message_handler(content_types=['text'])
def error_command(message):
    """Функция выполняется в случае ввода несуществующей команды
    :param message:
    :return: None
    """
    bot.send_message(message.chat.id, 'Вы ввели несуществующую '
                                      'команду, чтоб узнать список доступных команд, '
                                      'введите /help')


if __name__ == '__main__':
    """Запуск телеграм-бота"""
    bot.polling(none_stop=True)