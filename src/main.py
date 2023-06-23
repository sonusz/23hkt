import traceback
import logging
from logger import init_logger
from openai_agent import GPCSAzureGPT3dot5TurboChat

from chat_hist import messages
from chat_hist import functions
from fact_check import curl_check

logger = init_logger('UT', logging.INFO)
my_azure_gpt35 = GPCSAzureGPT3dot5TurboChat(logger=logger)


def api_helper(user_input: str):
    messages.append({"role": "user", "content": user_input})
    response = my_azure_gpt35.completion(messages, max_tokens=4000)
    messages.append({"role": "assistant", "content": response})
    success, msg = exe_curl(messages)
    if success is True:
        print(messages[-1]["content"])
    else:
        print("We are running into some issue, please try again later.")
        return


def exe_curl(messages):
    success = False
    msg = ''
    try:
        retry = 3
        success = False
        while retry:
            if retry <= 0:
                print("OpenAI failed to generate correct curl command.")
                break
            retry -= 1
            everything_looks_good = True
            msg = ''

            for line in messages[-1]["content"].split('\n'):
                if line.startswith('curl'):
                    everything_looks_good, msg = curl_check(line)
                    if everything_looks_good is False:
                        break
            if everything_looks_good is False:
                sys_msg = "The curl command in your previous response does not work in a dry run. "
                if msg:
                    sys_msg += f"Here is the error message: {msg}"
                sys_msg += "Correct the curl and return exactly the same as your previous response, only with the updated " \
                           "curl command and nothing else."
                messages.append({"role": "system", "content": sys_msg})
            else:
                success = True
                break
    except Exception as e:
        print(f"Exception in exe_curl: {str(e)}, {traceback.format_exc()}")
        pass
    finally:
        return success, msg

