"""
Библиотека базовых классов и методов для удобной работы бота ВКонтакте и GitHub.

Автор: tankalxat34

ВКонтакте: https://vk.com/tankalxat34

"""
import json
import requests
from io import BytesIO
import base64
import random

import vk_api
import vk_api.keyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload

from justdotenv import DotEnv
env = DotEnv()


class ConnectGitHub:
    def __init__(self, repo, token=env.GITHUB_TOKEN, username=env.GITHUB_USERNAME):
        """Класс для работы с файлами на GitHub"""
        self.token = token
        self.username = username
        self.repo = repo
        self.auth = (self.username, self.token)
        self.url_file = "https://api.github.com/repos/{username}/{repo}/contents/{filepath}?ref={branch}"

    def get_user(self):
        """Возвращает информацию о пользователе"""
        r = requests.get('https://api.github.com/user', auth=self.auth)
        return r.json()

    def get_file(self, filepath, branch="main"):
        """Возвращает текст из текстового файла"""
        doc_response = requests.get(self.url_file.format(username=self.username, repo=self.repo, filepath=filepath, branch=branch), auth=self.auth).json()["content"]
        return base64.b64decode(doc_response).decode('utf-8')

    def get_image(self, filepath, branch="main"):
        """Возвращает читабельную ссылку на картинку
        Читабельная ссылка - при запросе по этой ссылке и получении атрибута content можно получить саму картинку"""
        response = requests.get(self.url_file.format(username=self.username, repo=self.repo, filepath=filepath, branch=branch), auth=self.auth).json()["download_url"]
        return response

    def _dirlist(self, dirpath="", branch="main"):
        """Список файлов в директории"""
        response = requests.get(self.url_file.format(username=self.username, repo=self.repo, filepath=dirpath, branch=branch), auth=self.auth).json()
        return response


def get_vk_image(filepath, branch="main"):
    """Возвращает строку в формате photo12345678_123455678_1234567890123456789"""
    # запрашиваем нужную картинку на GitHub
    url = github.get_image(filepath, branch)
    _image = requests.get(url, auth=github.auth).content

    # загружаем ее как байты
    bytes_f = BytesIO(_image)

    # загружаем картинку на сервера ВКонтакте и возвращаем строку доступа к ней,
    # которую можно передать в attachment метода send
    response = UPLOAD.photo_messages(bytes_f)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    return f"photo{owner_id}_{photo_id}_{access_key}"


# Установка соединения с GitHub и получение const.json
github = ConnectGitHub(env.GITHUB_REPO)
CONST_JSON = json.loads(github.get_file("const.json", "content"))

# Создание необходимых констант для общения с юзером
# сообщения, на которые реагирует бот при приветствии и выходе
HELLO_USER_MESSAGES = CONST_JSON["hello"].split(",")
QUIT_USER_MESSAGES = CONST_JSON["quit"].split(",")

# сообщения, которыми бот отвечает на сообщения приветствия от юзера
HELLO_ANSWER_MESSAGE = CONST_JSON["answers"]["hello"]
HELLO_ERROR_MESSAGE = CONST_JSON["answers"]["errorMessage"]

# Установка соединения с VK с помощью CONST_JSON["tokenVK"]
VK = vk_api.VkApi(token=CONST_JSON["tokenVK"])
LONGPOLL = VkLongPoll(VK)
UPLOAD = VkUpload(VK)

# Получение текста из файла help.txt ветки content
HELP_ADMIN = github.get_file("help.txt", "content")

# получение списка с поздравлениями
greetings_file = github.get_file("greetings.txt", "content").split("\n")

# получение текста сообщения Пасхалка
about_egg_file = github.get_file("about_egg.txt", "content")

# загружаем в ВК все картинки, которые есть в images в ветке content
IMAGES_LIST = []
lst_images = github._dirlist("images", "content")
for e in lst_images:
    IMAGES_LIST.append(get_vk_image(e["path"], "content"))

# загрузка секретной картинки на сервер ВК
SECRET_IMAGE = get_vk_image("secret.png", "content")

# здесь место для инициализации клавиатур
main_kb = vk_api.keyboard.VkKeyboard(one_time=False, inline=False)
main_kb.add_button(CONST_JSON["keyboards"]["main"]["greeting"]["text"], color=CONST_JSON["keyboards"]["main"]["greeting"]["color"])
main_kb.add_button(CONST_JSON["keyboards"]["main"]["card"]["text"], color=CONST_JSON["keyboards"]["main"]["card"]["color"])
main_kb.add_line()
main_kb.add_button(CONST_JSON["keyboards"]["main"]["about_egg_1"]["text"], color=CONST_JSON["keyboards"]["main"]["about_egg_1"]["color"])
main_kb.add_line()
main_kb.add_button(CONST_JSON["keyboards"]["main"]["author"]["text"], color=CONST_JSON["keyboards"]["main"]["author"]["color"])
json_main_kb = main_kb.get_keyboard()


class UserVK:
    def __init__(self, user_id):
        """Класс для работы с картинками и отправки сообщений"""
        self.user_id = user_id
        self.sex_list = [None, "женский", "мужской"]

    def get_name(self, type="first"):
        """Возвращает имя или фамилию написавшего"""
        tmp = VK.method('users.get', {'user_ids': self.user_id})
        if type == 'first' or type == 'last':
            try:
                return tmp[0][type+"_name"]
            except Exception:
                return 'ErrorName'

    def get_sex(self):
        """Возвращает пол пользователя"""
        return self.sex_list[VK.method("users.get", {"access_token": CONST_JSON["tokenVK"], "user_ids": self.user_id, "fields": "sex"})[0]["sex"]]

    def send(self, text, keyboard=None, attachment=None):
        """Старый и долгий метод. Отправляет сообщение"""
        return VK.method("messages.send",
                         {"user_id": self.user_id, "message": text, "random_id": random.randint(1, 10 ** 6),
                          "keyboard": keyboard, "attachment": attachment})


def send(user_id, text, keyboard=None, attachment=None):
    """Отправляет сообщение"""
    return VK.method("messages.send",
                     {"user_id": user_id, "message": text, "random_id": random.randint(1, 10 ** 6),
                      "keyboard": keyboard, "attachment": attachment})


if __name__ == "__main__":
    userVk = UserVK(int(CONST_JSON["bigBoss"]))
    print(userVk.get_name())