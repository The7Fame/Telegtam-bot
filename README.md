# Телеграм-бот для поиска отелей

Бот поможет подобрать нужный отель исходя из Вашего запроса. 

## Функционал бота

С помощью бота Вы можете реализовать следующее:

- подобрать отели с самой низкой и высокой стоимостью;
- подобрать отели согласно Вашим пожеланиям;
- посмотреть историю запросов.

## Команды бота

- /start - запуск бота;
- /lowprice — вывод самых дешёвых отелей;
- /highprice — вывод самых дорогих отелей;
- /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра;
- /history — вывод истории поиска отелей;
- /help - список команд и их описание.

## Requirements
- googletrans==3.1.0a0
- peewee==3.14.9
- pyTelegramBotAPI==4.4.0
- python-dateutil==2.8.2
- python-dotenv==0.19.2
- python-telegram-bot-calendar==1.0.5
- requests==2.27.1

Для установки библиотек выше необходимо написать следующую команду в терминале: 
pip install -r requirements.txt