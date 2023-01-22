import logging
from .exceptions import CancelRequestError, ValidateRequestError
from aiogram import types

logger = logging.getLogger(__name__)


class BaseChatResponse:
    def __await__(self):
        logger.debug('Start response await')
        res = yield self
        logger.debug('End response await, receive %s', res)
        return res


class ChatResponse(BaseChatResponse):
    cancel_cmd = '/cancel'
    on_cancel_text = 'Canceled'

    on_validate_error_text = 'Bad value'

    def __init__(self, *, on_cancel_text=None, **kwargs):
        self.send_request_params = kwargs

        self.on_cancel_text = on_cancel_text or self.on_cancel_text

    async def process_output_message(self, message: types.Message):
        pass

    async def process_input_message(self, message: types.Message):
        if message.text == self.cancel_cmd:
            raise CancelRequestError(self.on_cancel_text)

        self.validate_input_message(message)

    def validate_input_message(self, message):
        pass

    def modify_input_message(self, message: types.Message):
        return message


class TextRequest(ChatResponse):
    def __init__(self, **kwargs):
        super(TextRequest, self).__init__(**kwargs)

        self.value_one_of = []
        if 'reply_markup' in kwargs:
            for word_list in kwargs['reply_markup'].keyboard:
                self.value_one_of.extend(word_list)

    def validate_input_message(self, message):
        if self.value_one_of and message.text not in self.value_one_of:
            raise ValidateRequestError(f'Value must be one of: {", ".join(self.value_one_of)}')

        super().validate_input_message(message)

    async def process_output_message(self, message: types.Message):
        # from chat
        return await message.answer(**self.send_request_params)

    def modify_input_message(self, message: types.Message):
        return message.text


class IntRequest(TextRequest):
    on_validate_error_text = 'Wait integer'

    def validate_input_message(self, message):
        try:
            int(message.text)
        except ValueError:
            raise ValidateRequestError(self.on_validate_error_text)

        super(IntRequest, self).validate_input_message(message)

    def modify_input_message(self, message: types.Message):
        return int(message.text)
