import random
import re
import os
import sys

import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

words_by_level = {
    "easy": [
        {"ru": "кот", "en": "cat"},
        {"ru": "собака", "en": "dog"},
        {"ru": "яблоко", "en": "apple"},
        {"ru": "молоко", "en": "milk"},
    ],

    "medium": [
        {"ru": "банан", "en": "banana"},
        {"ru": "школа", "en": "school"},
        {"ru": "друг", "en": "friend"},
        {"ru": "окно", "en": "window"},
    ],

    "hard": [
        {"ru": "технология", "en": "technology"},
        {"ru": "университет", "en": "university"},
        {"ru": "информация", "en": "information"},
        {"ru": "произношение", "en": "pronunciation"},
    ]
}


DURATION = 5
SAMPLE_RATE = 44100
MAX_LIVES = 3
ROUNDS = 10

recognizer = sr.Recognizer()


def normalize(text):
    """Очищает распознанный текст."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def choose_level():
    print("\n🎮 ВЫБЕРИ УРОВЕНЬ СЛОЖНОСТИ")
    print("1. 🟢 Easy")
    print("2. 🟡 Medium")
    print("3. 🔴 Hard")

    levels = {
        "1": "easy",
        "2": "medium",
        "3": "hard"
    }

    while True:
        choice = input("\nТвой выбор: ")

        if choice in levels:
            return levels[choice]

        print("❌ Выбери 1, 2 или 3!")


def record_voice():
    """Записывает голос и распознаёт английскую речь."""

    print("\n Приготовься!")
    input("Нажми Enter, чтобы начать запись...")

    try:
        print(" ИДЁТ ЗАПИСЬ! ГОВОРИ ПО-АНГЛИЙСКИ!")

        recording = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        filename = "output.wav"
        wav.write(filename, SAMPLE_RATE, recording)

        print(" Запись завершена!")

        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)

        print(" Распознаём речь...")

        recognized = recognizer.recognize_google(
            audio,
            language="en-US"
        )

        return recognized

    except sr.UnknownValueError:
        print(" Не удалось распознать речь!")
        return None

    except sr.RequestError:
        print(" Ошибка сервиса распознавания.")
        print("Проверь подключение к интернету.")
        return None

    except Exception as error:
        print(f" Ошибка записи: {error}")
        return None


def play_game(level):
    words = words_by_level[level].copy()
    random.shuffle(words)

    score = 0
    lives = MAX_LIVES
    streak = 0
    mistakes = 0

    print("\n" + "=" * 40)
    print(" ИГРА НАЧИНАЕТСЯ!")
    print("=" * 40)

    for round_number, word in enumerate(words[:ROUNDS], start=1):

        if lives <= 0:
            break

        print(f"\n РАУНД {round_number}/{ROUNDS}")
        print("-" * 35)

        print(f"🇷🇺 Переведи слово: {word['ru']}")

        recognized = record_voice()

        if recognized is None:
            print(" Попробуем следующее слово.")
            continue

        print(f" Ты произнёс: {recognized}")

        answer = normalize(word["en"])
        player_answer = normalize(recognized)

        if player_answer == answer:

            streak += 1
            points = 10

            if streak >= 3:
                points += 5
                print("🔥 БОНУС ЗА СЕРИЮ +5!")

            score += points

            print(" ПРАВИЛЬНО!")
            print(f" +{points} очков")
            print(f" Серия правильных ответов: {streak}")

        else:
            lives -= 1
            mistakes += 1
            streak = 0

            print(" НЕПРАВИЛЬНО!")
            print(f"Правильный ответ: {word['en']}")
            print(f" Осталось жизней: {lives}")

        print(f"\n Счёт: {score}")
        print(f" Жизни: {lives}")

    print("\n" + "=" * 40)
    print(" ИГРА ЗАВЕРШЕНА!")
    print("=" * 40)

    if lives == 0:
        print(" GAME OVER!")
        print("У тебя закончились жизни.")

    else:
        print(" Ты завершил все раунды!")

    print(f"\n ТВОЙ РЕЗУЛЬТАТ: {score}")
    print(f" Ошибок: {mistakes}")

    if score >= 100:
        print("🥇 AMAZING! Отличное знание английского!")
    elif score >= 70:
        print("🥈 GREAT! Хороший результат!")
    elif score >= 40:
        print("🥉 NOT BAD! Продолжай тренироваться!")
    else:
        print(" KEEP LEARNING! Практика делает лучше!")


def main():
    print("""
╔══════════════════════════════════╗
║          🎙️ SPEAK MASTER         ║
║                                  ║
║       LEARN. SPEAK. WIN!         ║
╚══════════════════════════════════╝
    """)

    print("Добро пожаловать в SPEAK MASTER!")
    print("Твоя задача — произносить английские слова.")
    print("У тебя есть 3 жизни и 10 раундов.")
    print("За каждый правильный ответ дают 10 очков.")

    while True:

        level = choose_level()
        play_game(level)

        again = input("\n Сыграть ещё раз? (да/нет): ").lower().strip()

        if again not in ["да", "д", "yes", "y"]:
            print("\n Спасибо за игру! До встречи!")
            break


if __name__ == "__main__":
    main()
