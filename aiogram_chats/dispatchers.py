from aiogram import Dispatcher
from .handlers import ChatMessageHandler


class ChatDispatcher(Dispatcher):
    def __init__(self, *args, **kwargs):
        super(ChatDispatcher, self).__init__(*args, **kwargs)

        self.message_handlers = ChatMessageHandler(self, middleware_key='message')  # rewrite initial
