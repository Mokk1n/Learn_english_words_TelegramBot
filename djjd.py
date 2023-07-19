import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

bot = Bot(token='6006418421:AAGggMi5iEm2CBFG4QQj-GOGnAhEVhASkck')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    p = message.from_user.first_name
    print(p)
    await message.reply(
        f"Вітання {p}! Я бот для вивчення англійських слів. Напиши /help, щоб отримати список доступних команд")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    help_text = """
    Список доступних команд:
    /start - почати навчання
    /word - отримати нове слово
    /addword - додати нове слово до словника
    /list - список доступних слів
    /list_learn - список вивчених слів
    /test - перевірити знання слів
    /help - список доступних команд
    """
    await message.reply(help_text)


def get_user_dict(user_id):
    filename = f"user_{user_id}_words.json"
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_user_dict(user_id, dictionary):
    filename = f"user_{user_id}_words.json"
    with open(filename, "w") as file:
        json.dump(dictionary, file)


def get_user_dict1(user_id):
    filename = f"user_{user_id}_words_learn.json"
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_user_dict1(user_id, dictionary):
    filename = f"user_{user_id}_words_learn.json"
    with open(filename, "w") as file:
        json.dump(dictionary, file)


@dp.message_handler(commands=['word'])
async def word(message: types.Message):
    user_id = message.from_user.id
    dictionary = get_user_dict(user_id)

    if not dictionary:
        await message.reply("Немає доступних слів для навчання./help")
        return

    word = random.choice(list(dictionary.keys()))
    translation = dictionary[word]
    await message.reply(f"Твоє слово: {word}. Напиши переклад.")

    # Save the chosen word for comparison with the user's answer
    message.bot.current_word = (word, translation)


@dp.message_handler(commands=['addword'])
async def addword(message: types.Message):
    # Получаем новое слово и перевод от пользователя
    await message.reply("Введіть нове слово та його переклад через двокрапку (наприклад, apple:яблуко):")
    await dp.current_state().set_state('addword')


@dp.message_handler(state='addword')
async def process_addword(message: types.Message, state: types.ChatShared):
    # Получаем новое слово и перевод от пользователя
    word, translation = message.text.lower().split(':')

    user_id = message.from_user.id
    dictionary = get_user_dict(user_id)

    # Добавляем новое слово в словарь пользователя
    dictionary[word] = translation

    # Сохраняем словарь пользователя в файл
    save_user_dict(user_id, dictionary)

    # Отправляем подтверждение
    await message.reply(f"Слово {word} додано до словника!/help")

    # Возвращаемся в начальное состояние
    await state.finish()


@dp.message_handler(commands=['list'])
async def list_words(message: types.Message):
    user_id = message.from_user.id
    dictionary = get_user_dict(user_id)

    if not dictionary:
        await message.reply("У вас немає слів у словнику./help")
        return

    # Формируем текстовое сообщение со списком слов и их переводов
    text = "Список слів та їх перекладів, що містяться в вашому словнику:\n"
    for word, translation in dictionary.items():
        text += f"{word}: {translation}\n"

    # Отправляем сообщение пользователю
    await message.reply(text + "/help")


@dp.message_handler(commands=['list_learn'])
async def list_words(message: types.Message):
    user_id = message.from_user.id
    dictionary = get_user_dict1(user_id)

    if not dictionary:
        await message.reply("У вас немає слів у словнику./help")
        return

    # Формируем текстовое сообщение со списком слов и их переводов
    text = "Список слів та їх перекладів, що містяться в вашому словнику:\n"
    for word, translation in dictionary.items():
        text += f"{word}: {translation}\n"

    # Отправляем сообщение пользователю
    await message.reply(text + "/help")


@dp.message_handler(commands=['test'])
async def test_words(message: types.Message):
    user_id = message.from_user.id
    dictionary = get_user_dict(user_id)

    if not dictionary:
        await message.reply("Немає слів для перевірки.")
        return

    word = random.choice(list(dictionary.keys()))
    translation = dictionary[word]

    message.bot.current_word = (word, translation)

    await message.reply(f"Переклад слова: {word}. Напиши свій варіант перекладу.")


@dp.message_handler()
async def check_word(message: types.Message):
    word, translation = message.bot.current_word
    answer = message.text.lower()

    if answer == translation.lower():
        await message.reply("Добре, ти вгадав слово!")

        user_id = message.from_user.id
        dictionary = get_user_dict(user_id)

        del dictionary[word]
        save_user_dict(user_id, dictionary)
        user_id = message.from_user.id
        dictionary = get_user_dict1(user_id)

        # Добавляем новое слово в словарь пользователя
        dictionary[word] = translation

        # Сохраняем словарь пользователя в файл
        save_user_dict1(user_id, dictionary)

        # Отправляем подтверждение
        await message.reply(f"Слово {word} додано до словника!/help")
    else:
        await message.reply(f"На жаль, правильна відповідь: {translation}/help")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
