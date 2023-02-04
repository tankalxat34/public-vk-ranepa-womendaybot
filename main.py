#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Есть идея создать бота для девочек
То есть девочка переходит по ссылке, пишет боту, а он присылает ей рандомную открытку на 8 марта и какое-то поздравление
Открытки и поздравления сейчас в процессе

Девочка переходит по ссылке, дальше бот предлагает ей получить открытку или поздравление, девочка получает то,
что выбрала, потом можно еще выбрать. Можешь еще давать вопросы какие-то наводящие, например
"Привет, ты мальчик или девочка" , про курс или направление можно спросить

"""
import random
from vk_api.longpoll import VkEventType
import importlib
import botlib


HEADERS = {"user-agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.2"}


def _start():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            sent_message = event.text
            user_id = event.user_id

            # Обычные сообщения. Ответ на них приоритетнее

            # ответ на начать
            if sent_message.lower() in botlib.HELLO_USER_MESSAGES:
                botlib.send(user_id, botlib.HELLO_ANSWER_MESSAGE % botlib.UserVK(user_id).get_name(), keyboard=botlib.json_main_kb)

            # ответ на просьбу получить открытку
            elif sent_message.lower() == botlib.CONST_JSON["keyboards"]["main"]["card"]["text"].lower():
                botlib.send(user_id, botlib.CONST_JSON["answers"]["yourCard"], attachment=random.choice(botlib.IMAGES_LIST))

            # ответ на просьбу получить поздравление
            elif sent_message.lower() == botlib.CONST_JSON["keyboards"]["main"]["greeting"]["text"].lower():
                botlib.send(user_id, random.choice(botlib.greetings_file))

            # ответ на просьбу получить описание пасхалки
            elif sent_message.lower() == botlib.CONST_JSON["keyboards"]["main"]["about_egg_1"]["text"].lower():
                botlib.send(user_id, botlib.about_egg_file)

            # обработка секретного сообщения, которое могут получить только девушки
            elif sent_message.lower() == botlib.CONST_JSON["answers"]["secretTriggerMessage"].lower():
                if botlib.UserVK(user_id).get_sex() == "женский":
                    botlib.send(user_id, botlib.CONST_JSON["answers"]["secretMessage"] % botlib.UserVK(user_id).get_name(), attachment=botlib.SECRET_IMAGE)
                    botlib.send(int(botlib.CONST_JSON["bigBoss"]),
                                f"🎁 [id{user_id}|{botlib.UserVK(user_id).get_name()} {botlib.UserVK(user_id).get_name('last')}] нашла пасхалку!")
                else:
                    botlib.send(user_id, botlib.HELLO_ERROR_MESSAGE)

            # обработка команды АВТОР
            elif sent_message.lower() == botlib.CONST_JSON["keyboards"]["main"]["author"]["text"].lower():
                botlib.send(user_id, botlib.CONST_JSON["answers"]["author"])

            # команды администратора
            elif str(user_id) in botlib.CONST_JSON["adminList"].split(",") and sent_message.lower()[0] == "/":
                command = sent_message.lower().split()
                botlib.send(user_id, f"🍕 Вы запустили операцию: "+command[0])

                if int(user_id) != int(botlib.CONST_JSON["bigBoss"]):
                    botlib.send(int(botlib.CONST_JSON["bigBoss"]), f"🍕 Администратор [id{user_id}|{botlib.UserVK(user_id).get_name()} {botlib.UserVK(user_id).get_name('last')}] запустил операцию: "+command[0])

                if command[0] == "/обновить":
                    """Команда перезагружает текстовый и графический контент бота. 
                    Если были внесены изменения в ветке content, то надо выполнить эту команду.
                    
                    Команда останавливает бота до окончания операции!"""
                    importlib.reload(botlib)
                    botlib.send(user_id, "🍕 Обновление бота завершено")
                    if int(user_id) != int(botlib.CONST_JSON["bigBoss"]):
                        botlib.send(int(botlib.CONST_JSON["bigBoss"]),
                                f"🍕 Администратор [id{user_id}|{botlib.UserVK(user_id).get_name()} {botlib.UserVK(user_id).get_name('last')}] завершил операцию: " +
                                command[0])
                    raise ValueError(command[0])

                elif command[0] == "/статус":
                    """Команда показывает отправителю свой статус"""
                    botlib.send(user_id, "🍕 Вы являетесь администратором чат-бота")

                elif command[0] == "/помощь":
                    """Команда показывает всю основную информацию о боте"""
                    botlib.send(user_id, botlib.HELP_ADMIN)

                elif command[0] == "/список_админов":
                    """Команда отправляет список администраторов
                    
                    Команда останавливает бота до окончания операции!"""
                    admin_list = ""
                    for e in botlib.CONST_JSON["adminList"].split(","):
                        admin_list += f"[id{e}|{botlib.UserVK(int(e)).get_name()} {botlib.UserVK(int(e)).get_name('last')}]\n"
                    botlib.send(user_id, "🍕 Список админов чат-бота:\n" + admin_list)

                elif command[0] == "/количество_диалогов":
                    """Команда отправляет список написавших пользователей. Не выполнять без особенной необходимости!"""
                    response = botlib.VK.method("messages.getConversations", {"access_token": botlib.CONST_JSON["tokenVK"]})
                    botlib.send(user_id, f"🍕 Количество диалогов с сообществом на данный момент: {response['count']}")

                else:
                    botlib.send(user_id, f"🍕 Команда " + command[0] + " не найдена. Попробуйте написать /помощь, чтобы получить список доступных команд.")
            else:
                botlib.send(user_id, botlib.HELLO_ERROR_MESSAGE)


while True:
    try:
        vk = botlib.VK
        longpoll = botlib.LONGPOLL
        upload = botlib.UPLOAD
        print('Бот запущен!')
        print(__doc__)
        _start()
    except Exception:
        pass