from datetime import datetime


def period_price(day_in, day_out, price):
    """
    Функция считает стоимость проживания в отеле за ночь.
    :param date_in: дата заезда
    :param date_out: дата выезда
    :param price: стоимость проживания за один день
    :return: price_total стоимость проживания за период
        """
    day_in = datetime.strptime(str(day_in), "%Y-%m-%d")
    day_out = datetime.strptime(str(day_out), "%Y-%m-%d")
    date_delta = int((day_out - day_in).days)
    price_total = date_delta * price
    return int(price_total)