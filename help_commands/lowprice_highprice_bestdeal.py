from googletrans import Translator
import rapidapi
from db.users import User
from help_commands.res_w_photo_low_high import result_with_photo
from telebot import types
from db import model
from loader import bot
from help_commands import calendar_for_users, result_hotel, period_date_price
import re

translator = Translator()


def low_high_best_func(message):
    """Функция получает название города
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    bot.send_message(message.chat.id, 'Где ищем? ')
    bot.register_next_step_handler(message, check_in_dates)


def check_in_dates(message):
    """Функция переводит город на русский язык, если он был написан на английском,
    а также получает дату заезда и выезда
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    user.city = (translator.translate(message.text.lower(), dest='ru')).text
    return calendar_for_users.date_in(message)


def hotel_count(message):
    """Функция получает количество отелей
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    bot.send_message(message.chat.id, 'Количество отелей (не больше 5)')
    bot.register_next_step_handler(message, photos)


def photos(message):
    """Функция запрашивает необходдимость в фотографиях и проверяет количество отелей
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    HOTELS_NUM = message.text
    find = re.match(r'\d+', HOTELS_NUM)
    if find and int(HOTELS_NUM) > 5 or not find:
        bot.send_message(message.chat.id, 'Вы ввели неправильное число.')
        return hotel_count(message)

    user.hotel_count = message.text
    photo_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    photo_markup.add("да", "нет")
    bot.send_message(message.chat.id, "Нужны фотографии?\n", reply_markup=photo_markup)
    bot.register_next_step_handler(message, num_photo)


def num_photo(message):
    """Функция получает ответ от пользователя о необходимости фотографий,
    если фотографии не нужны, то выводит результат
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    if message.text.lower() == 'да':
        user.need_photo = message.text
        bot.send_message(message.chat.id, 'Введите количество фотографий (не больше 5)')
        bot.register_next_step_handler(message, result_with_photo)
    elif message.text.lower() == 'нет':
        user.need_photo = message.text
        bot.send_message(message.chat.id, 'Ищем согласно запросу.')
        search_city = rapidapi.get_city(city=user.city)  # получаем id города
        if search_city is None:
            bot.send_message(message.chat.id, 'Ничего не удалось найти \n'
                                              'Попробуйте ещё раз./help')
        else:
            search_hotel = rapidapi.get_hotel(city_id=search_city,
                                              count=user.hotel_count,
                                              data_in=user.check_in,
                                              data_out=user.check_out,
                                              command=user.command)  # получаем данные по отелям
            to_show = []#список отелей для вывода в каждой команде
            for i in range(int(user.hotel_count)):
                if 'ratePlan' in search_hotel[i]:
                    price = (search_hotel[i]["ratePlan"]['price']['current']).replace('$', '')
                    price_for_period = period_date_price.period_price(day_in=user.check_in,
                                                                      day_out=user.check_out,
                                                                      price=int(price))
                    info = result_hotel.info_hotel(search_hotel[i], price_for_period)
                    cheap_hotels = (str(i + 1) + info)
                    print(cheap_hotels)
                    user.hotels_res.append(search_hotel[i]["name"])
                    bot.send_message(message.chat.id, cheap_hotels)
                    to_show.append(search_hotel[i]["name"])
            bot.send_message(message.chat.id, 'Поиск завершён.\n'
                                              'Хорошего дня!')
            print(to_show)
            model.add_user_data(user.command, user.user_id, user.time_of_use, to_show)
    else:
        bot.send_message(message.chat.id, 'Неверная команда.\n'
                                          'Только да или нет.')
        bot.register_next_step_handler(message, num_photo)



