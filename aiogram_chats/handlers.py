import asyncio
import logging

from aiogram import types
from aiogram.dispatcher import filters as ag_filters, handler as ag_handlers

from .chats import Chat, ChatAsResponse
from .exceptions import CancelRequestError, ValidateRequestError
from .requests import ChatResponse

logger = logging.getLogger(__name__)


class ChatMessageHandler(ag_handlers.Handler):
    async def notify(self, message):
        """
        check if is just text, try find chat response and handle it
        todo: add filter for start chat, only one chat should be start for one message
        todo: process middleware for chat messages
        """
        update_chat_handler = None
        for handler_obj in self.handlers:
            if not isinstance(handler_obj.handler, Chat):
                continue

            if handler_obj.handler.is_have_chat(message):
                update_chat_handler = handler_obj
                break

            try:
                await ag_filters.check_filters(handler_obj.filters, (message,))
            except ag_filters.FilterNotPassed:
                continue

            if update_chat_handler is not None:
                raise ValueError(f'Bad filters, one more handler work with message {message}')

            update_chat_handler = handler_obj

        if update_chat_handler is not None:
            return await self.handle_chat(update_chat_handler.handler, message)

        return await super().notify(message)

    async def handle_chat(self, chat_handler: Chat, update):
        send_into_chat = None
        current_chat, chat_request = chat_handler.get_or_create_chat(update)

        if isinstance(chat_request, ChatResponse):
            try:
                await chat_request.process_input_message(update)
            except ValidateRequestError as err:
                await update.reply(err.reason)
                chat_handler.set_chat(update, current_chat, chat_request)
                return
            except CancelRequestError as err:
                await update.reply(err.reason, reply_markup=types.ReplyKeyboardRemove())
                return

            send_into_chat = chat_request.modify_input_message(update)

        if isinstance(chat_request, ChatAsResponse):
            raise NotImplementedError('need go on chat lists, target is last')

        return await self._process_chat(chat_handler, current_chat, send_into_chat, update)

    async def _process_chat(self, chat: Chat, current_chat, send_into_chat, message):
        previous_chat = None
        while True:
            try:
                r = current_chat.send(send_into_chat)
            except StopIteration:
                if chat.is_have_chat(message):
                    current_chat, _ = chat.get_or_create_chat(message)
                    continue
                else:
                    break

            if isinstance(r, ChatResponse):
                await r.process_output_message(message)
                chat.set_chat(message, current_chat, r)
                return

            if isinstance(r, ChatAsResponse):
                chat.set_chat(message, current_chat, r)
                previous_chat = chat  # где то нужно сохранить прошлый чат чтобы спуститься вниз
                chat, current_chat = r.chat, r.chat_future
                current_chat, _ = r.chat.get_or_create_chat(message, chat)  # create only
                send_into_chat = None

            if asyncio.isfuture(r):
                send_into_chat = await self._wait_future(r)
                continue

            send_into_chat = r  # скорее всего это нормальное значение и корутина кончилась

    @staticmethod
    async def _wait_future(fut: asyncio.Future, timeout_sec=5, iterations=50):
        # todo: move to helpers
        iteration_leave = iterations
        while iteration_leave > 0:
            try:
                return fut.result()
            except asyncio.InvalidStateError:
                logger.debug('Wait future, leave %s iteration', iteration_leave)

            iteration_leave -= 1
            await asyncio.sleep(timeout_sec / iterations)

        raise TimeoutError('%s seconds elapsed while waiting %s', timeout_sec, fut)
