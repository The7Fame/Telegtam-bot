from peewee import *
from db.users import *
import telebot
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

db = SqliteDatabase('history.db')


class BaseModel(Model):
    class Meta:
        database = db


class User_data(BaseModel):
    telegram_id = IntegerField()
    name = CharField()
    date_info = CharField()
    hotel_result = CharField()


with db:
    User_data.create_table()


def without_simbols(list1: str) -> str:
    """
        Функция принимает значение 'название отелей' из базы данных и заменяет символы
        :param list1:
        :return: list1
        """
    return str(list1).replace('[', '').replace(']', '').replace("'", '')


def add_user_data(command, user_id, date, result) -> None:
    """
    Функция создает запись в базе данных.
    :param command:
    :param user_id:
    :param date:
    :param result:
    :return:
    """
    with db:
        User_data.create(name=command,
                         telegram_id=user_id,
                         date_info=date,
                         hotel_result=result)


def req_history(message: telebot.types.Message) -> None:
    """
    Функция, которая отправляет пользователю историю запросов.
    :param message:
    :return: None
    """
    user = User.get_user(message.from_user.id)
    with db:
        for data in User_data.select().where(User_data.telegram_id == user.user_id):
            history_for_user = f"Команда: {data.name}\n" \
                               f"Дата и время обращения: {data.date_info}\n" \
                               f"Список найденных отелей:\n{(without_simbols(data.hotel_result))}"
            bot.send_message(user.user_id, history_for_user)