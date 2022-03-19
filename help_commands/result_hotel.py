def info_hotel(hotel, total_price):
    """ Функция, которая выводит конечный вариант отеля для пользователя
    :param hotel
    :param total_price
    :return: result
    """
    result = (' отель: \nНазвание: ' + hotel["name"] +
              '\nАдрес: ' + hotel["address"]["locality"] + ', ' +
              hotel["address"]["region"] +
              '\nОт ' + hotel["landmarks"][0]['label'] + ' ' +
              ' расстояние: ' + ' ' + hotel["landmarks"][0]['distance'] +
              '\nЦена за сутки: ' + hotel["ratePlan"]['price']['current'] +
              '\nЦена за выбранный период: ' + '$' + str(total_price) +
              '\nСайт: https://ru.hotels.com/ho' + str(hotel["id"]))
    return result
