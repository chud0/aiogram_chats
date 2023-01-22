"""
like https://github.com/aiogram/aiogram/blob/master/examples/finite_state_machine_example.py
"""

import logging

import aiogram
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage as aiogram_MemoryStorage

import aiogram_chats

logger = logging.getLogger(__name__)


API_TOKEN = 'BOT TOKEN HERE'

bot = aiogram.Bot(token=API_TOKEN)
storage = aiogram_MemoryStorage()
dp = aiogram_chats.ChatDispatcher(bot, storage=storage)


@dp.message_handler()
@aiogram_chats.aiogram_chat
async def test_handler(message: aiogram.types.Message):
    logger.debug('In test handler')
    name = await aiogram_chats.TextRequest(text='Hi there! Whats your name?')
    logger.info('Receive name: %s', name)

    age = await aiogram_chats.IntRequest(text='How old are you?')
    logger.info('Receive age: %s', age)

    allowed_genders = ['Male', 'Female']
    markup = aiogram.types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*allowed_genders)
    gender = await aiogram_chats.TextRequest(text='What is your gender?', reply_markup=markup)
    logger.info('Receive city: %s', gender)

    await bot.send_message(
        message.chat.id,
        md.text(
            md.text('Hi! Nice to meet you,', md.bold(name)),
            md.text('Age:', md.code(age)),
            md.text('Gender:', gender),
            sep='\n',
        ),
        reply_markup=aiogram.types.ReplyKeyboardRemove(),
        parse_mode=aiogram.types.ParseMode.MARKDOWN,
    )
    logger.info('End test handler')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )
    aiogram.executor.start_polling(dp, skip_updates=True)
