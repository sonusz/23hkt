import traceback
import logging
from openai_agent import GPCSAzureGPT3dot5TurboChat
from env import *

from chat_hist import messages
from chat_hist import functions
from fact_check import curl_check

def api_helper(openai_model, user_input: str):
    messages.append({"role": "user", "content": user_input})
    response = openai_model.completion(messages, max_tokens=4000)
    messages.append({"role": "assistant", "content": response})
    success, msg = exe_curl(messages, openai_model)
    if success is True and not msg:
        print(f'GPT: {messages[-1]["content"]}')
    elif success is True and msg:
        messages.append({"role": "assistant", "content": "Let me check ..."})
        print(f'GPT: {messages[-1]["content"]}')
        messages.append({"role": "system", "content": "The user provided real token, please help the customer analysis the results: "})
        messages.append({"role": "system", "content": msg})
        response = openai_model.completion(messages, max_tokens=4000)
        messages.append({"role": "assistant", "content": response})
        print(f'GPT: {messages[-1]["content"]}')
    else:
        print("System: We are running into some issue, please try again later.")
        return


def exe_curl(messages, openai_model):
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
                response = openai_model.completion(messages, max_tokens=4000)
                messages.append({"role": "assistant", "content": response})
            else:
                success = True
                break
    except Exception as e:
        print(f"Exception in exe_curl: {str(e)}, {traceback.format_exc()}")
        pass
    finally:
        return success, msg

def main():
    logger = logging.getLogger()
    my_azure_gpt35 = GPCSAzureGPT3dot5TurboChat(logger=logger, temperature=0.8)
    welcome = "This is an AI agent to guide you use the getPrismaAccessIP API."
    messages.append({"role": "assistant", "content": welcome})
    print(f"GPT: {welcome}")
    while True:
        print("You: ", end="")
        api_helper(my_azure_gpt35, input())

if __name__ == '__main__':
    main()