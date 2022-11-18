from simple_bot import Bot

import random
import schedule
import time


class ScheduleBot(Bot):
    pet_names = [
        "котёнок",
        "зайчонок",
        "малыш",
        "кингурёнок",
        "солнышко",
        "котик",
        "чертёнок",
        "мышонок",
        "хомячок",
        "пёсик",
        "пупсик",
        "золотце",
        "милый",
        "медвежонок",
        "членастик",
        "писюн",
        "бяка"
    ]

    def __init__(self):
        super().__init__()
        self.create_schedule()
        while True:
            schedule.run_pending()

    def wish_good_morning(self):
        pet_name = self.pet_names[random.randint(0, len(self.pet_names) - 1)]
        phrases = [
            "Доброе утро, {}! Как спалось?".format(pet_name),
            "Утро, {}! Какой план у тебя на день?".format(pet_name),
            "Утро, {}".format(pet_name),
            "Доброе утро, {}, какой сон тебе снился сегодня?".format(pet_name),
            "Утро, уже позавтракал?".format(pet_name)
        ]
        message = phrases[random.randint(0, len(phrases) - 1)]
        self.send_message(message_text=message)

    def talk_about_lunch(self):
        pet_name = self.pet_names[random.randint(0, len(self.pet_names) - 1)]
        phrases = [
            "Угадай, чем я сегодня обедала, {}".format(pet_name),
            "Приятного аппетита, {}!".format(pet_name),
            "А что ты любишь кушать, {}?".format(pet_name),
            "Что ты ел сегодня, {}?".format(pet_name),
        ]
        message = phrases[random.randint(0, len(phrases) - 1)]
        self.send_message(message_text=message)

    def ask_how_the_day_was(self):
        pet_name = self.pet_names[random.randint(0, len(self.pet_names) - 1)]
        phrases = [
            "Как твой день проходит, {}?".format(pet_name),
            "Чем занимался сегодня, {}?".format(pet_name),
            "Признавайся, что делал весь день, {}?".format(pet_name),
            "Чего успел натворить за сегодня, {}?".format(pet_name)
        ]
        message = phrases[random.randint(0, len(phrases) - 1)]
        self.send_message(message_text=message)

    def wish_good_night(self):
        pet_name = self.pet_names[random.randint(0, len(self.pet_names) - 1)]
        phrases = [
            "Доброй ночи, {}!".format(pet_name),
            "Сладких снов, {})".format(pet_name),
            "Cпи крепко, {}".format(pet_name),
            "Cпокнойно ночи тебе, {}, завтра продолжим".format(pet_name)
        ]
        message = phrases[random.randint(0, len(phrases) - 1)]
        self.send_message(message_text=message)

    def create_schedule(self):
        morning_time = "0" + str(random.randint(7, 9)) + ":" + str(random.randint(10, 59))
        schedule.every().day.at(morning_time).do(self.wish_good_morning())
        lunch_time = str(random.randint(11, 13)) + ":" + str(random.randint(10, 59))
        schedule.every().day.at(lunch_time).do(self.talk_about_lunch())
        evening_time = str(random.randint(18, 20)) + ":" + str(random.randint(10, 59))
        schedule.every().day.at(evening_time).do(self.ask_how_the_day_was())
        night_time = str(random.randint(22, 23)) + ":" + str(random.randint(10, 59))
        schedule.every().day.at(night_time).do(self.wish_good_night())
        schedule.every().day.at("00:00").do(self.restart_schedule)
        print(f"Расписание на {time.strftime('%d.%m.%Y')}"
              f"\n{morning_time}\n{lunch_time}\n{evening_time}\n{night_time}\n")

    def restart_schedule(self):
        schedule.clear()
        self.create_schedule()
