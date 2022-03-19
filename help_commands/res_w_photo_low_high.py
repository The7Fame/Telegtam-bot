from telebot.types import InputMediaPhoto
import rapidapi
from db.users import User
from loader import bot
from db import model
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
        bot.send_message(message.chat.id, 'Вы ввели неправильное число.')
        bot.send_message(message.from_user.id,
                                     'Введите количество фотографий, '
                                     'которые необходимо вывести в результате (не больше 5): ')
        bot.register_next_step_handler(message, result_with_photo)
    else:
        bot.send_message(message.chat.id, 'Ищем согласно запросу.')
        user.num_photo = message.text
        search_city = rapidapi.get_city(city=user.city)  # получаем id города
        if search_city is None:
            bot.send_message(message.chat.id, 'Ничего не удалось найти \n'
                                              'Попробуйте ещё раз./help')
        else:
            search_hotel = rapidapi.get_hotel(city_id=search_city,
                                              count=user.hotel_count,
                                              data_in=user.check_in,
                                              data_out=user.check_out,
                                              command=user.command)  # получаем данные по отелю или отелям
            to_show = []#список отелей для вывода в каждой команде
            for i in range(int(user.hotel_count)):
                if 'ratePlan' in search_hotel[i]:
                    price = (search_hotel[i]["ratePlan"]['price']['current']).replace('$', '')
                    price_for_period = period_date_price.period_price(day_in=user.check_in,
                                                                      day_out=user.check_out,
                                                                      price=int(price))
                    info = result_hotel.info_hotel(hotel=search_hotel[i],
                                                   total_price=price_for_period)
                    cheap_or_expensive_hotel = (str(i + 1) + info)
                    print(cheap_or_expensive_hotel)
                    user.hotels_res.append(search_hotel[i]["name"])
                    to_show.append(search_hotel[i]["name"])
                    bot.send_message(message.chat.id, cheap_or_expensive_hotel)
                    search_photo = rapidapi.get_photo(id_hotel=search_hotel[i]["id"]) #получаем id
                    media = []
                    for j in range(int(user.num_photo)):
                        media.append(InputMediaPhoto(
                            (search_photo["hotelImages"][j]['baseUrl']).format(size='z')))#получаем фотографии
                    bot.send_media_group(message.chat.id, media)
            bot.send_message(message.chat.id, 'Поиск завершён. '
                                              '\n Хорошего дня!')
            print(to_show)
            model.add_user_data(user.command, user.user_id, user.time_of_use, to_show)