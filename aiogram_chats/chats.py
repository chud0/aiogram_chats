from collections import defaultdict
from typing import Generator


class ChatAsResponse:
    # fixme: make internal?
    def __init__(self, chat, chat_future):
        self.chat = chat
        self.chat_future = chat_future


class Chat(Generator):
    def __init__(self, cb):
        self.cb_func = cb
        self._chats = defaultdict(list)  # key: (message_author, chat) value: list chats

    def send(self, args):
        coro, update = args
        from_chat = coro.send(update)
        return from_chat

    def throw(self, type=None, value=None, traceback=None):
        raise StopIteration

    def __call__(self, *args, **kwargs):
        return ChatAsResponse(self, self.cb_func(*args, **kwargs))

    @staticmethod
    def _build_key_from_update(message):
        return message.from_user.id, message.chat.id

    def is_have_chat(self, message):
        return bool(self._chats[self._build_key_from_update(message)])

    def get_or_create_chat(self, message, chat_state=None):
        if not self._chats[self._build_key_from_update(message)]:
            return self.cb_func(message), chat_state
        return self._chats[self._build_key_from_update(message)].pop()

    def set_chat(self, message, chat, awaitable_response):
        return self._chats[self._build_key_from_update(message)].append((chat, awaitable_response))


def aiogram_chat(cb):
    """ decorator, simple way for create chat handler """
    return Chat(cb)
