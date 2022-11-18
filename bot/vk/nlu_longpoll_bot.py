from longpoll_bot import LongPollBot  # базовый класс бота из файла longpoll_bot

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from vk_api.longpoll import VkEventType
import zipfile
import os.path
import random
import nltk
import json


class NLUULongPoolBot(LongPollBot):
    vectorizer = None
    classifier = None
    dataset = {}
    threshold = 0.7
    stats = {"intent": 0, "generative": 0, "failure": 0}

    bot_config = {
        "intents": {
            "hello": {
                "example": ["Привет", "Здравствуйте", "Добрый день"],
                "responses": ["Привет", "Здравствуйте", "Предлагаю сразу к делу :)"]
            },
            "bye": {
                "example": ["Пока", "До свидания", "Увидимся"],
                "responses": ["Пока", "Веди себя хорошо"]
            },
        },
        "failure_phrases": [
            "Не знаю что сказать даже",
            "Меня не научили так отвечать",
            "Я не знаю, как отвечать на такое"
        ]
    }

    def __init__(self):
        super().__init__()
        with open("bot_corpus/bot_config.json", encoding="utf-8") as file:
            self.bot_config = json.load(file)
            self.create_bot_config_corpus()
            self.create_bot_dialog_dataset()

    def run_long_poll(self):
        print("Запуск бота")
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if event.from_user:
                    bot_response = self.get_bot_response(event.text)
                    self.send_message(receiver_user_id=event.user_id, message_text=bot_response)
                    print(self.stats)

    def get_bot_response(self, request: str):
        intent = self.get_intent(request)
        if intent:
            self.stats["intent"] += 1
            return self.get_response_by_intent(intent)
        response = self.get_generative_response(request)
        if response:
            self.stats["generative"] += 1
            return response
        self.stats["failure"] += 1
        return self.get_failure_phrase()

    def get_intent(self, request: str):
        question_probabilities = self.classifier.predict_proba(self.vectorizer.transform([request]))[0]
        best_intent_probability = max(question_probabilities)
        if best_intent_probability > self.threshold:
            best_intent_index = list(question_probabilities).index(best_intent_probability)
            best_intent = self.classifier.classes_[best_intent_index]
            return best_intent
        return None

    def get_response_by_intent(self, intent: str):
        phrases = self.bot_config["intents"][intent]["responses"]
        return random.choice(phrases)

    def normalize_request(self, request):
        normalized_request = request.lower().strip()
        alphabet = " -1234567890йцукенгшщзхъфывапролджэёячсмитьбю"
        normalized_request = "".join(character for character in normalized_request if character in alphabet)
        return normalized_request

    def get_generative_response(self, request: str):
        phrase = self.normalize_request(request)
        words = phrase.split(" ")
        mini_dataset = []
        for word in words:
            if word in self.dataset:
                mini_dataset += self.dataset[word]
        candidates = []

        for question, answer in mini_dataset:
            if abs(len(question) - len(request)) / len(question) < 0.4:
                distance = nltk.edit_distance(question, request)
                score = distance / len(question)
                if score < 0.4:
                    candidates.append([question, answer, score])
        if candidates:
            return min(candidates, key=lambda candidate: candidate[0])[1]
        return None

    def get_failure_phrase(self):
        phrases = self.bot_config["failure_phrases"]
        return random.choice(phrases)

    def create_bot_config_corpus(self):
        corpus = []
        y = []

        for intent, intent_data in self.bot_config["intents"].items():
            for example in intent_data["examples"]:
                corpus.append(example)
                y.append(intent)
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
        x = self.vectorizer.fit_transform(corpus)
        self.classifier = LogisticRegression()
        self.classifier.fit(x, y)
        print("Обучение на файле конфигурация завершено")

    def create_bot_dialog_dataset(self):
        if not os.path.isfile("bot_corpus/dialogues.txt"):
            with zipfile.ZipFile("bot_corpus/dialogues.zip", "r") as zip_file:
                zip_file.extractall("bot_corpus")
                print("Распаковка датасета завершена")
            with open("bot_corpus/dialogues.txt", encoding="utf-8") as file:
                content = file.read()
            dialogues = content.split("\n\n")
            questions = set()

            for dialogue in dialogues:
                phrases = dialogue.split("\n")[:2]
                if len(phrases) == 2:
                    question, answer = phrases
                    question = self.normalize_request(question[2:])
                    answer = answer[2:]

                    if question and question not in questions:
                        questions.add(question)
                        words = question.split(" ")
                        for word in words:
                            if word not in self.dataset:
                                self.dataset[word] = []
                            self.dataset[word].append([question, answer])
            too_popular = set()
            for word in self.dataset:
                if len(self.dataset[word]) > 10000:
                    too_popular.add(word)
            for word in too_popular:
                self.dataset.pop(word)

            print("Загрузка датасетов диалогов завершена")
