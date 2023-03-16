#!venv/bin/python
import config
from state import GlobalState

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext, filters
from aiogram.utils import executor

storage = MemoryStorage()

TG_TOKEN = config.TOKEN

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot, storage=storage)
TELEGRAM_SUPPORT_CHAT_ID = config.TELEGRAM_SUPPORT_CHAT_ID


# @dp.message_handler(commands='start', state=None)
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        'Приветствуем!\n\n'
        'Расскажите нам о своей проблеме как можно подробнее и отправьте скриншоты, если нужно.\n'
        'Постарайтесь описать вашу проблему в одном сообщении.\n\n'
        'Также обратите внимание, что ожидание ответа может занять больше 24 часов.'
    )
    await state.set_state(GlobalState.forward)


async def forward_to_chat(message: types.Message, state: FSMContext):
    mes = (
        'Новое сообщение от пользователя\n'
        f'user_id: {message.from_user.id}\n'
        f'name: {message.from_user.first_name} {message.from_user.last_name}\n'
        f'username: {message.from_user.username}'
    )
    await bot.send_message(chat_id=TELEGRAM_SUPPORT_CHAT_ID, text=mes)
    await bot.copy_message(
            message_id=message.message_id,
            chat_id=TELEGRAM_SUPPORT_CHAT_ID,
            from_chat_id=message.chat.id,
            reply_markup=InlineKeyboardMarkup(row_width=5).add(
                InlineKeyboardButton(text='Ответить 🙋‍♂️', callback_data=f'answer:{message.chat.id}'))
        )
    async with state.proxy() as data:
        data['client_id'] = message.from_user.id
    await message.answer(
        'Ваше сообщение отправлено в наш чат техподдержки.✅\n\n'
        'Если хотите задать еще вопрос - напишите его ниже 🔽'
    )



async def what_admin(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['admin_id'] = call.from_user.id
        data['client_id'] = call.data.split(':')[-1]
    await call.message.answer(f'👨‍💻 Отвечает пользователь: {call.from_user.username}')
    try:
        await call.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(row_width=5).add(
                        InlineKeyboardButton(text='Ответить еще раз 🤷‍♂️', callback_data=f'answer:{data["client_id"]}')))
    except:
        print(1)
    await state.set_state(GlobalState.wait_admin_ans)


async def wait_admin_ans(message: types.Message, state: FSMContext):
    print(message.text)
    async with state.proxy() as data:
        await bot.copy_message(
            message_id=message.message_id,
            chat_id=data['client_id'],
            from_chat_id=message.chat.id,
        )
    await message.answer('Сообщение отправлено пользователю ✅')
    await state.finish()


dp.register_message_handler(start, filters.ChatTypeFilter(chat_type=['private',]), state=None)
dp.register_message_handler(forward_to_chat, content_types=[
    types.ContentType.ANY
], state=GlobalState.forward)
dp.register_callback_query_handler(what_admin, text_contains='answer:', state='*')
dp.register_message_handler(
    wait_admin_ans, filters.IDFilter(chat_id=TELEGRAM_SUPPORT_CHAT_ID), state=GlobalState.wait_admin_ans,
    content_types=[types.ContentType.ANY]
)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)