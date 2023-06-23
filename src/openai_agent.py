import os
import openai
import traceback
from sys import stdout
import asyncio
from aiohttp import ClientSession

def get_my_event_loop(logger):
    my_loop = asyncio.get_event_loop()
    logger.debug(f'asyncio.get_event_loop()')
    if my_loop.is_closed():
        logger.debug(f'my_loop.is_closed()')
        my_loop = asyncio.new_event_loop()
        logger.debug(f'asyncio.new_event_loop()')
    return my_loop



class OpenAIBase():
    def __init__(self, logger, temperature=0.5):
        self.logger = logger
        self.temperature = 0.5
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.model = 'gpt-3.5-turbo'

    def completion(self, messages: list, *args, **kwargs):
        response = ''
        try:
            _res = openai.ChatCompletion.create(
                model=self.model,
                stream=False,
                messages=messages,
                temperature=self.temperature
            )
            response = _res['choices'][0]['message'].get('content', '')
        except Exception as e:
            self.logger.error(f'Exception in chat_response! {str(e)}, traceback: {traceback.format_exc()}')
        finally:
            return response


class GPCSAzureGPT3dot5TurboChat(OpenAIBase):
    def __init__(self, logger, temperature=0.5):
        super(GPCSAzureGPT3dot5TurboChat, self).__init__(logger, temperature)
        resource_name = 'gpcs-nw-west-europe'
        openai.api_base = f'https://{resource_name}.openai.azure.com/'
        openai.api_type = 'azure'
        openai.api_key = os.environ["OPENAI_API_KEY"]
        openai.api_version = '2023-05-15'
        self.deployment_id = 'gpcs-nw-west-europe-poc'

    def completion(self, messages: list, *args, **kwargs):
        response = ''
        try:
            _res = openai.ChatCompletion.create(
                deployment_id=self.deployment_id,
                stream=False,
                messages=messages,
                temperature=self.temperature
            )
            response = _res['choices'][0]['message'].get('content', '')
        except Exception as e:
            self.logger.error(f'Exception in chat_response! {str(e)}, traceback: {traceback.format_exc()}')
        finally:
            return response

    async def async_stream_completion(self, messages: list, *args, **kwargs):
        response = ''
        try:
            openai.aiosession.set(ClientSession())
            _res = await openai.ChatCompletion.acreate(
                deployment_id=self.deployment_id,
                stream=True,
                messages=messages,
                temperature=self.temperature
            )
            print("GPT: ", end="")
            async for line in _res:
                print(line['choices'][0]['delta'].get('content', ''), end='', flush=True)
                response += line['choices'][0]['delta'].get('content', '')
            print("")
            await openai.aiosession.get().close()
        except Exception as e:
            self.logger.error(f'Exception in chat_response! {str(e)}, traceback: {traceback.format_exc()}')
        finally:
            return response

    def stream_completion(self, *args, **kwargs):
        my_loop = get_my_event_loop(self.logger)
        return my_loop.run_until_complete(self.async_stream_completion(*args, **kwargs))