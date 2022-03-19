from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta
from db.users import User
from loader import bot
from help_commands import lowprice_highprice_bestdeal, bestdeal


LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def date_in(message):
    user = User.get_user(message.from_user.id)
    calendar, step = DetailedTelegramCalendar(calendar_id=1,
                                              current_date=date.today(),
                                              min_date=date.today(),
                                              locale="ru").build()
    bot.send_message(message.chat.id,
                     f"Выберите {LSTEP[step]} заезда",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def handle_date_in(call):
    user = User.get_user(call.from_user.id)
    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 current_date=date.today(),
                                                 min_date=date.today(),
                                                 locale="ru").process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]} заезда",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user.check_in = result
        bot.edit_message_text(f"Дата заезда: {user.check_in}",
                              call.message.chat.id,
                              call.message.message_id)
        calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                                  min_date=user.check_in + timedelta(days=1),
                                                  locale="ru").build()
        bot.send_message(user.user_id,
                         f"Выберите {LSTEP[step]} выезда",
                         reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def handle_departure_date(call):
    user = User.get_user(call.message.chat.id)
    result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                 min_date=user.check_in + timedelta(days=1),
                                                 locale="ru").process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]} выезда",
                              user.user_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        user.check_out = result
        bot.send_message(call.message.chat.id, f"Дата выезда: {user.check_out}")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if user.command == 'дешёвые отели' or user.command == 'дорогие отели':
            return lowprice_highprice_bestdeal.hotel_count(call.message)
        else:
            return bestdeal.hotel_count(call.message)