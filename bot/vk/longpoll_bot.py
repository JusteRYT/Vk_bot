from simple_bot import Bot

from vk_api.longpoll import VkLongPoll, VkEventType


class LongPollBot(Bot):
    long_poll = None

    def __init__(self):
        super().__init__()
        self.long_poll = VkLongPoll(self.vk_session)

    def run_long_poll(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.text == "Привет" or event.text == "Здравствуй":
                    if event.from_user:
                        self.send_message(receiver_user_id=event.user_id, message_text="И тебе привет")
                    elif event.from_chat:
                        self.send_message(receiver_user_id=event.chat_id, message_text="Всем привет")
