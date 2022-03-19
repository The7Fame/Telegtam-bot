from googletrans import Translator
import rapidapi
from help_commands.res_w_photo_bestdeal import result_with_photo
from telebot import types
from loader import bot
from db.users import User
from db import model
from help_commands import result_hotel, period_date_price
import re

translator = Translator()


def hotel_count(message):
    """Функция получает количество отелей
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    bot.send_message(message.chat.id, 'Количество отелей (не больше 5): ')
    bot.register_next_step_handler(message, min_price)


def min_price(message):
    """Функция получает минимальную цену в $ и проверяет количество отелей
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    HOTELS_NUM = message.text
    find = re.match(r'\d+', HOTELS_NUM)
    if int(HOTELS_NUM) and find > 5 or not find:
        bot.send_message(message.chat.id, 'Вы ввели неправильное число.')
        return hotel_count(message)
    user.hotel_count = message.text
    bot.send_message(message.from_user.id, 'Минимальная цена отеля (в $) ')
    bot.register_next_step_handler(message, max_price)


def max_price(message):
    """Функция получает максимальную цену в $
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    user.price_min = message.text
    bot.send_message(message.from_user.id, 'Максимальная цена отеля (в $)')
    bot.register_next_step_handler(message, min_distance)


def min_distance(message):
    """Функция получает минимальное расстояние в км и проверяет стоимости
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    user.price_max = message.text
    if int(user.price_min) > int(user.price_max):
        bot.send_message(message.chat.id, 'Максимальная цена не может быть меньше минимальной.'
                                            '\nПопробуйте еще раз.')
        return min_price(message)
    bot.send_message(message.from_user.id, 'Минимальное расстояние до центра(в км.) ')
    bot.register_next_step_handler(message, max_distance)


def max_distance(message):
    """Функция получает максимальное расстояние в км
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    user.distance_min = message.text
    bot.send_message(message.from_user.id, 'Максимальное расстояние до центра(в км.) ')
    bot.register_next_step_handler(message, check_distance)


def check_distance(message):
    """Функция проверяет расстояние и делает запрос о фотографиях
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    user.distance_max = message.text
    if float(user.distance_min) > float(user.distance_max):
        bot.send_message(message.chat.id, 'Максимальное расстояние не может быть меньше минимального.'
                                            '\nПопробуйте еще раз.')
        return min_distance(message)
    photo_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    photo_markup.add("да", "нет")
    bot.send_message(message.from_user.id, "Нужны фотографии?", reply_markup=photo_markup)
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
        bot.send_message(message.from_user.id,
                                     'Введите количество фотографий (не больше 5)')
        bot.register_next_step_handler(message, result_with_photo)
    elif message.text.lower() == 'нет':
        user.need_photo = message.text
        bot.send_message(message.chat.id, 'Ищем согласно запросу.')
        search_city = rapidapi.get_city(city=user.city)  # получаем id города
        if search_city is None:
            bot.send_message(message.chat.id, 'Ничего не удалось найти \n'
                                              'Попробуйте ещё раз./help')
        else:
            search_hotel = rapidapi.get_hotel_bestdeal(city_id=search_city,
                                                   count=user.hotel_count,
                                                   data_in=user.check_in,
                                                   data_out=user.check_out,
                                                   price_min=user.price_min,
                                                   price_max=user.price_max)  # получаем отели
            to_show = []#список отелей для вывода в каждой команде
            for i in range(int(user.hotel_count)):
                dist = search_hotel[i]["landmarks"][0]['distance']
                print(dist)
                dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))
                if float(user.distance_min) < dist_from_cent < float(user.distance_max) and 'ratePlan' in search_hotel[i]:
                    price = (search_hotel[i]["ratePlan"]['price']['current']).replace('$', '')
                    price_for_period = period_date_price.period_price(user.check_in, user.check_out, int(price))
                    info = result_hotel.info_hotel(search_hotel[i], price_for_period)
                    best_hotels = (str(i + 1) + info)
                    print(best_hotels)
                    user.hotels_res.append(search_hotel[i]["name"])
                    to_show.append(search_hotel[i]["name"])
                    bot.send_message(message.chat.id, best_hotels)
            bot.send_message(message.chat.id, 'Поиск завершён. '
                                          '\n Хорошего дня!')
            print(to_show)
            model.add_user_data(user.command, user.user_id, user.time_of_use, to_show)
    else:
        bot.send_message(message.chat.id, 'Неверная команда.'
                                          '\n Только да или нет.')
        bot.register_next_step_handler(message, num_photo)