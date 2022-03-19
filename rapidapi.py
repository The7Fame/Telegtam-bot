import requests
from config import headers
import json
import re


url_locations = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_hotels = "https://hotels4.p.rapidapi.com/properties/list"
url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
headers = headers


def request_to_api(url, headers, querystring):
    """
    Функция делает запрос к API.
    :param url
    :param headers
    :param querystring
    :return:
    """
    try:
        response = requests.request("GET",
                                    url,
                                    headers=headers,
                                    params=querystring,
                                    timeout=20)
        if response.status_code == requests.codes.ok:
            return response
    except requests.Timeout:
        print('Время ожидания превышено')
    except requests.HTTPError as err:
        code = err.response.status_code
        print(f"Ошибка url: {url}, code: {code}")


def get_city(city):
    """
    Функция определяет локацию
    :param city:
    :return:
    """
    querystring = {'query': city,
                   'currency': 'USD',
                   'locale': "ru_RU"}
    result = request_to_api(url=url_locations,
                            headers=headers,
                            querystring=querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, result.text)
    if find:
        data = json.loads(f"{{{find[0]}}}")
    try:
        city_id = data['entities'][0]['destinationId']
        print(city_id)
        return city_id
    except IndexError:
        print('Не нахожу город')
        return None



def get_hotel(city_id, count, data_in, data_out, command):
    """
    Функция получает отель по команде 'дорогие отели' и 'дешёвые отели'
    :param city_id:
    :param count:
    :param data_in:
    :param data_out:
    :param command:
    :return:
    """
    querystring = {"destinationId": city_id,
                   "pageNumber": "1",
                   "pageSize": count,
                   "checkIn": data_in,
                   "checkOut": data_out,
                   "adults1": "1",
                   "sortOrder": "PRICE",
                   "locale": "ru_RU",
                   "currency": "USD"}
    if command == 'дорогие отели':
        querystring['sortOrder'] = 'PRICE_HIGHEST_FIRST'
    hotel_response = request_to_api(url=url_hotels,
                                    headers=headers,
                                    querystring=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination")'
    find = re.search(pattern, hotel_response.text)
    if find:
        data_hotel = json.loads(f"{{{find[0]}}}")
    result = data_hotel["results"]
    print(result)
    return result


def get_hotel_bestdeal(city_id, count, data_in, data_out, price_min, price_max):
    """
    Функция получает отель по команде 'Ваш запрос на отель'
    :param city_id:
    :param count:
    :param data_in:
    :param data_out:
    :param price_min:
    :param price_max:
    :return:
    """
    querystring = {"destinationId": city_id,
                   "pageNumber": "1",
                   "pageSize": count,
                   "checkIn": data_in,
                   "checkOut": data_out,
                   "adults1": "1",
                   "priceMin": price_min,
                   "priceMax": price_max,
                   "sortOrder": "PRICE",
                   "locale": "ru_RU",
                   "currency": "USD"}
    hotel_response_best = request_to_api(url=url_hotels,
                                         headers=headers,
                                         querystring=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination")'
    find = re.search(pattern, hotel_response_best.text)
    if find:
       data_hotel = json.loads(f"{{{find[0]}}}")
    try:
        result = data_hotel["results"]
        print(result)
        return result
    except UnboundLocalError:
        print('Не нахожу отели по заданным параметрам')
        return None


def get_photo(id_hotel):
    """
    Функция получает фотографии
    :param id_hotel:
    :return:
    """
    querystring = {"id": id_hotel}
    photo_response = request_to_api(url=url_photos,
                                    headers=headers,
                                    querystring=querystring)
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages")'
    find = re.search(pattern, photo_response.text)
    if find:
        data_photo = json.loads(f"{{{find[0]}}}")
    result = data_photo
    print(result)
    return result


