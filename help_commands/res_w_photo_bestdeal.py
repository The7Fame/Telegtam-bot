from telebot.types import InputMediaPhoto
import rapidapi
from db.users import User
from db import model
from loader import bot
from help_commands import result_hotel, period_date_price


def result_with_photo(message):
    """Функция проверяет правильность введённого количества фотографий,
    в случае правильного ввода, выводит результат работы телеграм-бота с фотографиями
    :param message:
    :return:
    """
    user = User.get_user(message.from_user.id)
    PHOTO_NUM = int(message.text)
    if PHOTO_NUM > 5:
        bot.send_message(message.chat.id, 'Вы ввели неправильное число.\n'
                                          'Введите количество фотографий (не больше 5)')
        bot.register_next_step_handler(message, result_with_photo)
    else:
        bot.send_message(message.chat.id, 'Ищем согласно запросу.')
        user.num_photo = message.text
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
            if search_hotel is None:
                bot.send_message(message.chat.id, 'Ничего не удалось найти \n'
                                                  'Попробуйте ещё раз./help')
            else:

                to_show = []#список отелей для вывода в каждой команде
                for i in range(int(user.hotel_count)):
                    dist = search_hotel[i]["landmarks"][0]['distance']
                    print(dist)
                    dist_from_cent = float(dist.replace(' км', '').replace(',', '.'))
                    if float(user.distance_min) < dist_from_cent < float(user.distance_max) \
                        and 'ratePlan' in search_hotel[i]:
                        price = (search_hotel[i]["ratePlan"]['price']['current']).replace('$', '')
                        price_for_period = period_date_price.period_price(day_in=user.check_in,
                                                                          day_out=user.check_out,
                                                                          price=int(price))
                        info = result_hotel.info_hotel(hotel=search_hotel[i],
                                                       total_price=price_for_period)
                        best_hotels_photo = (str(i + 1) + info)
                        print(best_hotels_photo)
                        user.hotels_res.append(search_hotel[i]["name"])
                        to_show.append(search_hotel[i]["name"])
                        bot.send_message(message.chat.id, best_hotels_photo)
                        search_photo = rapidapi.get_photo(id_hotel=search_hotel[i]["id"])  # получаем id
                        media = []
                        for j in range(int(user.num_photo)):
                            media.append(InputMediaPhoto(
                                (search_photo["hotelImages"][j]['baseUrl']).format(size='z')))  # получаем фотографии
                        bot.send_media_group(message.chat.id, media)
                bot.send_message(message.chat.id, 'Поиск завершён. '
                                                  '\n Хорошего дня!')
                print(to_show)
                model.add_user_data(user.command, user.user_id, user.time_of_use, to_show)