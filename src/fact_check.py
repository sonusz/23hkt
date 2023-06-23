import os
import shlex
import subprocess
import json
import traceback
from termcolor import colored

def curl_check(cmd):
    dry_run = False
    print(colored('Debug: curl dry run check', 'red'))
    if '<TOKEN>' in cmd:
        dry_run = True
        cmd = cmd.replace('<TOKEN>', f'{os.environ["TOKEN"]}')
    print(colored(f'Debug: {cmd}','red'))
    args = shlex.split(cmd)
    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    try:
        #print(f"Dry run result: {stdout}")
        r = json.loads(stdout)
        if r.get('status') != 'success':
            err_msg = r.get('result', 'Server responded without error message')
            print(colored(f'Debug: curl dry run check failed, {err_msg}', 'red'))
            return False, err_msg
        else:
            if dry_run:
                print(colored('Debug: curl dry run check passed', 'red'))
                return True, ''
            else:
                print(colored('Debug: curl passed', 'red'))
                return True, json.dumps(r)
    except Exception as e:
        print(colored(f'Debug: curl dry run check failed: Exception: str({e}), trace_back: {traceback.format_exc()}', 'red'))
        return False, f'Exception: str({e}), trace_back: {traceback.format_exc()}'

