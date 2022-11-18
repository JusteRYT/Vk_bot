import vk_api
import vk_api.vk_api
from vk_api.utils import get_random_id
from dotenv import load_dotenv
import os


class Bot:
    vk_session = None
    vk_api_access = None
    authorized = False
    default_user_id = None

    def __init__(self):
        load_dotenv()
        self.vk_api_access = self.do_auth()

        if self.vk_api_access is not None:
            self.authorized = True
        self.default_user_id = os.getenv("USER_ID")

    def do_auth(self):
        token = os.getenv("ACCESS_TOKEN")
        try:
            self.vk_session = vk_api.VkApi(token=token)
            return self.vk_session.get_api()
        except Exception as error:
            print(error)
            return None

    def send_message(self, receiver_user_id: str = None, message_text: str = "Тестовое сообщение"):
        if not self.authorized:
            print("Unauthorized. Check if ACCESS_TOKEN is valid")
            return
        if receiver_user_id is None:
            receiver_user_id = self.default_user_id

        try:
            self.vk_api_access.messages.send(user_id=receiver_user_id, message=message_text, random_id=get_random_id())
            print(f"Сообщение отправлено для ID {receiver_user_id} с текстом: {message_text}")
        except Exception as error:
            print(error)
