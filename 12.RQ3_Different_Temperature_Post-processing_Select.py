import copy
import time

import pandas as pd

from cache_result import cache

from code_complete_flow.huggingface_api import flow_huggingface_complete
from evaluation import get_complete_rq1_result
from evaluation.sim import sim, calculate_similarity_score
from get_dataset import add_function_huge_code, get_function_from_code
from models import code_line2str
from tools import get_code_first_line, timer

import requests
import json

import threading
lock = threading.Lock()


@cache('cache/select', exclude=['func_name', 'source_code'])
def predict(code_list: list[str]):
    url = "http://localhost:8001/predict"

    payload = json.dumps({
        "code_list": code_list
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        return response.json()['predict']
    except:
        return 0

@cache('cache/select')
def select_best_line(complete_line_result, pre_code_list, lcs_wight = 0.5, led_wight = 0.5, pre_code = None):

    best_line_score = 0
    best_line_index = -1
    predict_list = []

    for i, line in enumerate(complete_line_result):
        predict_list.append(str(pre_code) + '\n' + str(line))

    best_line_index = predict(predict_list)

    best_line = complete_line_result[best_line_index]

    return best_line, best_line_score / len(complete_line_result)

def merge_complete_result(lcs_wight = 0.5, led_wight = 0.5, model="google/gemma-7b", max_tokens = 50, prompt_max_tokens = 600):

    result = {}
    title = []

    for i in range(1, 17, 3):
    # for i in range(16, 0, -3):
        temperature = i / 10
        print(f"进行temperature {temperature}")
        title.append(f"{model} random={i}")
        huge_code_list, count_result, max_token, prompt_max_token = flow_huggingface_complete(max_tokens=max_tokens,
                                                                                             prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=lcs_wight, led_weight=led_wight, model=model, random=1, temperature=temperature)

        for huge_code in huge_code_list:
            key = huge_code.version_dir + huge_code.file_name
            if key not in result:
                result[key] = []
            result[key].append(huge_code)


    return result, title


from concurrent.futures import ThreadPoolExecutor, as_completed
def clean_filename(filename):
    invalid_chars = '\/:*?"<>|'
    cleaned_filename = ''.join('_' if c in invalid_chars else c for c in filename)
    return cleaned_filename.strip()

def process_one(key, result, lcs_wight, led_wight):
    complete_line_result = []
    # pre_code_list = []
    for index, huge_code in enumerate(result[key]):
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        complete_line_result.append(complete_line)


    pre_code = get_function_from_code(code_line2str(result[key][0].huge_content_list), code_line2str(result[key][0].huge_content_list_pre))
    # pre_code = add_function_huge_code(result[key][0]).function_code_pre_str
    print("pre_code:", pre_code)
    # 获取时间戳
    if pre_code == "":
        time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        with open(f"log/{time_stamp}.txt", "w", encoding='utf-8') as f:
            f.write(code_line2str(result[key][0].huge_content_list_pre))
        with open(f"log/{time_stamp}_all.txt", "w", encoding='utf-8') as f:
            f.write(result[key][0].huge_content_str)

    best_line, best_score = select_best_line(complete_line_result, None,  lcs_wight=lcs_wight, led_wight=led_wight, pre_code=pre_code)
    result[key][0].complete.complete_code = best_line
    return result[key][0]

def get_best_huge_code_list(result, lcs_wight=0.5, led_wight=0.5):
    best_huge_code_list = []

    with ThreadPoolExecutor(max_workers=1) as executor:
        # 使用map函数将任务分配给线程池中的线程
        futures = {executor.submit(process_one, key, result, lcs_wight, led_wight): key for key in result}

        for future in as_completed(futures):
            best_huge_code_list.append(future.result())

    return best_huge_code_list


@cache("cache/select/select_best_complete/{model}")
def select_best_complete(lcs_wight = 0.5, led_wight = 0.5, model="google/gemma-7b", newpayload={}, max_workers=3, max_tokens = 50, prompt_max_tokens = 600):
    result, title = merge_complete_result(model=model, max_tokens = max_tokens, prompt_max_tokens = prompt_max_tokens)

    count_result_list = {}
    descriptions = []
    huge_code_result = {}

    best_huge_code_list = get_best_huge_code_list(result)


    for i in range(1, 17, 3):
    # for i in range(16, 0, -3):
        temperature = i / 10
        huge_code_list, count_result, max_token, prompt_max_token = flow_huggingface_complete(max_tokens=max_tokens,
                                                                                             prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=lcs_wight, led_weight=led_wight, model=model, random=1, newpayload=newpayload, max_workers=max_workers, temperature=temperature)

        # count_result_list.append(count_result.to_dict())
        count_result_list[temperature] = count_result.to_dict()
        descriptions.append(f"{model} temperature={temperature}")
        for huge_code in huge_code_list:
            key = huge_code.version_dir + huge_code.file_name
            if key not in huge_code_result:
                huge_code_result[key] = []
            huge_code_result[key].append(huge_code)

    best_huge_code_list = calculate_similarity_score(best_huge_code_list, lcs_weight = lcs_wight, led_weight = 1-lcs_wight)
    count_result = get_complete_rq1_result(best_huge_code_list)
    # count_result_list.append(count_result.to_dict())
    count_result_list['model'] = count_result.to_dict()
    descriptions.append("从n个中用训练的模型选择出来的最佳补全")

    return count_result_list


models = ['openai/gpt-3.5-turbo-instruct',
          'google/gemma-7b', 'codellama/CodeLlama-13b-hf',
          'bigcode/starcoder2-15b', 'Salesforce/codegen-350M-multi']

models_name = ['OpenAI-GPT3.5',
               'Gemma-7b', 'CodeLlama-13b-hf',
               'StarCoder2-15b', 'CodeGEN-350M']

def get_data_list_wrong():

    data_list = {}
    for model in models:
        data_list[model] = select_best_complete(model=model)

    print("原始", json.dumps(data_list))

    models_list = data_list.keys()
    for model in models_list:
        for k in data_list[model].keys():
            model_data = data_list[model][k]
            data_list[model][k] = model_data['补全接近错误']
    print(json.dumps(data_list))
    return data_list


def get_data_list_right():
    data_list = {}
    for model in models:
        data_list[model] = select_best_complete(model=model)

    print(data_list)

    models_list = data_list.keys()
    for model in models_list:
        for k in data_list[model].keys():
            model_data = data_list[model][k]

            data_list[model][k] = model_data['补全接近正确']
    print(json.dumps(data_list))
    return data_list


def nearly_corrent():
    data_list = {}
    for model in models:
        data_list[model] = select_best_complete(model=model)

    print(data_list)
    all_data_list = copy.deepcopy(data_list)
    models_list = data_list.keys()
    for model in models_list:
        for k in data_list[model].keys():
            model_data = data_list[model][k]
            data_list[model][k] = model_data['补全接近正确'] + model_data['补全完全正确']  # model_data['补全接近正确']
            all_data_list[model][k] = model_data['补全接近正确'] + model_data['补全接近错误'] + model_data['补全完全正确'] + model_data['补全完全错误']

    print(json.dumps(data_list))
    print(json.dumps(all_data_list))

    df = pd.DataFrame(data_list)
    df_all = pd.DataFrame(all_data_list)
    columns_map = dict(zip(models, models_name))

    df.rename(columns=columns_map, inplace=True)
    df_all.rename(columns=columns_map, inplace=True)

    df = df.T
    df_all = df_all.T

    percentage = (df / df_all * 100).round(1).astype(str) + '\%'

    df = df.astype(str).add('/') + df_all.astype(str) + '(' +percentage + ')'
    print(df)

    df.columns = [col.replace('_', r'\_') if isinstance(col, str) else col for col in df.columns]

    # Replace underscores in index labels if your index is of type string
    if df.index.dtype == 'object':
        df.index = df.index.str.replace('_', r'\_', regex=False)
    # Assuming 'df' is your DataFrame
    df = df.T
    styled_df = df.style  # Here, you can chain styling options as needed

    latex_table = styled_df.to_latex(
        # column_format='lcc',
        column_format='l' + 'c' * len(df.columns),
        caption='Same Models with the Different Parameters Nearly Corrent',
        label='Same Models with the Different Parameters Nearly Corrent',
        position_float='centering',
        hrules=True,  # To add horizontal rules, similar to \toprule, \midrule, and \bottomrule in booktabs
    )
    print("latex:")
    print(latex_table)


if __name__ == '__main__':
    nearly_corrent()