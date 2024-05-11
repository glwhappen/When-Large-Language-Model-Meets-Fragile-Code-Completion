import json
import random
import threading
import time
import traceback

import requests
import os

import code_complete
from cache_result import cache
from code_complete.openai_completion import reduce_token_length
from code_complete.token_tools import get_openai_token_len
from models import Complete
from tools.ConfigManager import ConfigManager

headers = {"Authorization": "Bearer hf_xxx"}

config_manager = ConfigManager()
key_list = config_manager.get_param('huggingface', 'key_list', [
    'hf_xxx', # glw 1
    'hf_xxx', # glw 2
])


# os.environ['CURL_CA_BUNDLE'] = ''
# os.environ["http_proxy"] = "http://127.0.0.1:7890"
# os.environ["https_proxy"] = "http://127.0.0.1:7890"



def query(payload, model, key = None):
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    if key is None:
        key = random.choices(key_list)[0]
    print(key)
    headers['Authorization'] = f"Bearer {key}"
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

lock = threading.Lock()

def check(model, newpayload={}):
    payload = {
            "inputs": 'hello',
            "options": {
                "use_cache": False,
            },
            "parameters": {"max_new_tokens": 10}
        }
    payload = payload | newpayload
    print("执行请求", model)
    for key in key_list:
        output = query(payload, model, key) # type: str {'error': 'Model Salesforce/codegen-2B-multi is currently loading', 'estimated_time': 227.7208709716797}
        print(output)
        if 'error' in output and output['error'].find('is currently loading') != -1:
            print(output)
            print("进行等待", model)
            estimated_time = output['estimated_time']
            time.sleep(estimated_time)
        print("检查通过", model, key)
@cache(cache_dir='./cache/completion/huggingface/api_codegen/{model}/{random}')
def api_codegen(code: str, model = "Salesforce/codegen-350M-multi", random: int = 1, newplayload={}):
    res = ""
    payload = {
        "model": model,
        "params": {
            "text_inputs": code,
            "do_sample": True,
            "top_k": 10,
            "temperature": 0.1,
            "top_p": 0.95,
            "num_return_sequences": 1,
            "max_length": 200
        }
    }
    # print("payload", payload)
    # print("newplayload", newplayload)
    payload["params"] = payload["params"] | newplayload
    # print("合并", payload)
    config_manager = ConfigManager()
    url = config_manager.get_param('huggingface', 'api_codegen_url', 'http://localhost:5001/generate')
    try:
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        print(response.text)
        output = response.json()
        with lock:
            pass
            print(output)

        result: str = output[0]['generated_text']
        if result.startswith(code):
            res = result.split(code)[1]
        else:
            res = result
        with lock:
            pass
            print(res)
    except Exception as e:
        print('api 发生错误', e)
        # 打印堆栈
        traceback.print_exc()
        raise

    if res == None:
        print("error 没有任何补全结果", res)
        raise "error 没有任何补全结果"

    # Extracting and printing the 'generated_text' content
    return res

@cache(cache_dir='./cache/completion/huggingface/{model}/{random}')
def api(code: str, model = "google/gemma-7b", random: int = 1, newplayload={}):
    res = ""
    payload = {
            "inputs": code,
            "options": {
                "use_cache": False,
            }
        }
    payload = payload | newplayload

    try:
        output = query(payload, model)

        with lock:
            pass
            print(output)

        result: str = output[0]['generated_text']
        if result.startswith(code):
            res = result.split(code)[1]
        else:
            res = result
        with lock:
            pass
            print(res)
    except Exception as e:
        print('api 发生错误', e)
        raise

    if res == None:
        print("error 没有任何补全结果", res)
        raise "error 没有任何补全结果"

    # Extracting and printing the 'generated_text' content
    return res


def complete(code, max_tokens=200, prompt_max_tokens = 1000, model='google/gemma-7b', random = 1, newpayload = {}, temperature = 0.7) -> Complete:

    # 兼容其他接口
    if model == 'openai/gpt-3.5-turbo-instruct':
        # if newpayload =
        try:
            return code_complete.openai_completion.complete_random(random=random, code=code, temperature=temperature, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model="gpt-3.5-turbo-instruct")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise  # 重新抛出捕获到的异常

    if model == 'chatglm3':
        from code_complete.chatglm import complete
        return complete(code=code, max_tokens=50, prompt_max_tokens=300)

    if model == 'Salesforce/codegen-350M-multi-false':
        # 如果code的token长度大于了prompt_max_tokens，那么删除第一行，直到token长度小于prompt_max_tokens
        code = reduce_token_length(code, prompt_max_tokens)
        newpayload = newpayload | {
            "max_length": prompt_max_tokens + max_tokens
        }
        response = api_codegen(code=code, model="Salesforce/codegen-350M-multi", random=random, newplayload=newpayload)
    else:
        # 如果code的token长度大于了prompt_max_tokens，那么删除第一行，直到token长度小于prompt_max_tokens
        code:str = reduce_token_length(code, prompt_max_tokens)
        print('\n'.join(code.split('\n')[-3:]))
        newpayload = {"parameters": {"max_new_tokens": max_tokens, "temperature": temperature}}
        try:
            response = api(code, model, random, newpayload)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise  # 重新抛出捕获到的异常

    return Complete(
        row_code=code,
        complete_code=response,
        complete_tokens=get_openai_token_len(response),
        prompt_tokens=get_openai_token_len(code),
    )

if __name__ == '__main__':
    code = """
    public static boolean equal(Polygon p1, Polygon p2) {
        if (p1 == null) {
            return (p2 == null);
        }
        if (p2 == null) {
            return false;
        }
        if (p1.npoints != p2.npoints) {
            return false;
        }
        if (!Arrays.equals(p1.xpoints, p2.xpoints)) {
            return false;
        }
        if (!Arrays.equals(p1.ypoints, p2.ypoints)) {
            return false;
        }
        return true;
    }

    /**
     * Tests two polygons for equality.  If both are <code>null</code> this
     * method returns <code>true</code>.
     *
     * @param p1  path 1 (<code>null</code> permitted).
     * @param p2  path 2 (<code>null</code> permitted).
     *
     * @return A boolean.
     */
    public static boolean equal(GeneralPath p1, GeneralPath p2) {
        if (p1 == null) {
            return (p2 == null);
        }
        if (p2 == null) {
            return false;
        }
        if (p1.getWindingRule() != p2.getWindingRule()) {
            return false;
        }
        PathIterator iterator1 = p1.getPathIterator(null);
        """
    # for i in range(10):
    #     print(i)
    # check('Salesforce/codegen-2B-mono', newpayload={"parameters":{"max_new_tokens":20}})
    # print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="Salesforce/codegen-350M-multi", random=25, newpayload={"parameters":{"max_new_tokens":50}}).complete_code)
    # print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="Salesforce/codegen-350M-multi", random=26, newpayload={"parameters":{"max_new_tokens":50, 'temperature': 3}}).complete_code)
    print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="bigscience/bloom", temperature=0.1,
                   random=22).complete_code)  # bigcode/starcoder2-15b
    # print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="bigscience/bloom", random=22).complete_code) # bigcode/starcoder2-15b
    # print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="bigcode/starcoder2-15b", random=16).complete_code)

    # print(complete(code=code, max_tokens=50, prompt_max_tokens=300, model="Salesforce/codegen2-1B",
    #                random=22).complete_code)  # bigcode/starcoder2-15b

    # print(complete(code=code, max_tokens=500, prompt_max_tokens=300, model="Salesforce/codegen-350M-multi",
    #                random=16, newpayload={'temperature': 0.1, "max_length":500}).complete_code)