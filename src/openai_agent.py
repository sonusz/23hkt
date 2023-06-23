import os
import openai
import traceback


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