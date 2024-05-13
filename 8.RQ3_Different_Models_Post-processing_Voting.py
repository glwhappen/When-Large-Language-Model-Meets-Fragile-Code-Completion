import copy
import os

import pandas as pd
from matplotlib import pyplot as plt

from cache_result import cache

from code_complete_flow.huggingface_api import flow_huggingface_complete
from evaluation import get_complete_rq1_result
from evaluation.sim import sim, calculate_similarity_score

from models import code_line2str
from tools import get_code_first_line
from tools.experiment import save_csv, save_figure



import threading
lock = threading.Lock()

def merge_complete_result(lcs_wight = 0.5, led_wight = 0.5, models=["google/gemma-7b"], temperature=0.7, max_tokens = 50, prompt_max_tokens = 600):
    result = {}
    title = []


    for model in models:
        print(f"temperature {temperature}")
        title.append(f"{model} random={1}")
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

@cache('cache/voting')
def select_best_line(complete_line_result, lcs_wight = 0.5, led_wight = 0.5):

    best_line_score = 0
    best_line_index = -1

    for i, line in enumerate(complete_line_result):
        current_score = 0

        for other_line in complete_line_result:
                current_score += sim(line, other_line, lcs_weight=lcs_wight, led_weight=led_wight)

        if current_score > best_line_score:
            best_line_score = current_score
            best_line_index = i


    best_line = complete_line_result[best_line_index]

    return best_line, best_line_score / len(complete_line_result)

def process_one(key, result, lcs_wight, led_wight):
    complete_line_result = []
    for index, huge_code in enumerate(result[key]):
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        complete_line_result.append(complete_line)

    best_line, best_score = select_best_line(complete_line_result, lcs_wight=lcs_wight, led_wight=led_wight)
    result[key][0].complete.complete_code = best_line
    return result[key][0]
@cache("cache/voting/temperature/get_best_huge_code_list")
def get_best_huge_code_list(result, lcs_wight=0.5, led_wight=0.5):
    best_huge_code_list = []


    with ThreadPoolExecutor() as executor:

        futures = {executor.submit(process_one, key, result, lcs_wight, led_wight): key for key in result}

        for future in as_completed(futures):
            best_huge_code_list.append(future.result())

    return best_huge_code_list



@cache("cache/voting/select_best_complete/{temperature}")
def select_best_complete(lcs_wight = 0.5, led_wight = 0.5, models=["google/gemma-7b"], newpayload={}, temperature=0.7, max_workers=3, max_tokens = 50, prompt_max_tokens = 600):
    result, title = merge_complete_result(models=models, max_tokens = max_tokens, prompt_max_tokens = prompt_max_tokens, temperature=temperature)

    count_result_list = {}
    descriptions = []
    huge_code_result = {}

    best_huge_code_list = get_best_huge_code_list(result)


    for model in models:

        huge_code_list, count_result, max_token, prompt_max_token = flow_huggingface_complete(max_tokens=max_tokens,
                                                                                             prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=lcs_wight, led_weight=led_wight, model=model, random=1, newpayload=newpayload, max_workers=max_workers, temperature=temperature)

        count_result_list[model] = count_result.to_dict()
        descriptions.append(f"{model} temperature={temperature}")
        for huge_code in huge_code_list:
            key = huge_code.version_dir + huge_code.file_name
            if key not in huge_code_result:
                huge_code_result[key] = []
            huge_code_result[key].append(huge_code)

    best_huge_code_list = calculate_similarity_score(best_huge_code_list, lcs_weight = lcs_wight, led_weight = 1-lcs_wight)
    count_result = get_complete_rq1_result(best_huge_code_list)
    count_result_list['voting'] = count_result.to_dict()
    descriptions.append("voting")
    for huge_code in best_huge_code_list:
        key = huge_code.version_dir + huge_code.file_name
        if key not in huge_code_result:
            huge_code_result[key] = []
        huge_code_result[key].append(huge_code)
    for key, value in huge_code_result.items():
        # print(key, len(value))
        huge_code_base = value[0]
        huge_line = get_code_first_line.get_line(code_line2str(huge_code_base.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code_base.right_content_list_complete))
        # print(sim(right_line, value[1].complete.complete_code))
        openai = get_code_first_line.get_line(value[0].complete.complete_code)
        selecter = value[1].complete.complete_code
        # if sim(right_line, selecter) < 0.9:
        #     continue

        if sim(huge_line, openai) < 0.8:
            continue
        # if get_code_first_line.get_line(value[0].complete.complete_code) == value[1].complete.complete_code:
        #     continue
        print(f"pre:{code_line2str(huge_code_base.huge_content_list_pre[-40:])}")
        print("buggy line:", huge_line)
        print("fixed line:", right_line)
        print("     openai:", openai)
        print("  selecter:", selecter)
        print("===========")

    print(count_result_list)
    return count_result_list


    df = pd.DataFrame(count_result_list)

    df['description'] = descriptions
    df.drop('总量', axis=1, inplace=True)

    print(df)
    # 获取文件名，不带后缀
    file_name = os.path.basename(__file__).split('.')[0] + clean_filename(model)

    save_csv(df, file_name)

    df_transposed = df.set_index('description').T

    # Plotting the transposed DataFrame
    ax = df_transposed.plot(kind='bar', figsize=(12, 10))
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(f'使用投票规则从n个不同模型温度为{temperature}里面挑选一个')
    plt.ylabel('数量')
    plt.xlabel('Metrics')
    plt.xticks(rotation=45)  # Rotating x-axis labels for better readability
    plt.legend(title=f'max_tokens = {max_tokens}, prompt_max_tokens = {prompt_max_tokens}, lcs_weight = 0.5, led_weight = 0.5')

    # 添加每个柱子的数值
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', rotation=45)  # 倾斜45度

    save_figure(plt, file_name)
    plt.show()

models = ['openai/gpt-3.5-turbo-instruct',
          'google/gemma-7b', 'codellama/CodeLlama-13b-hf',
          'bigcode/starcoder2-15b', 'Salesforce/codegen-350M-multi']

models_name = ['OpenAI-GPT3.5',
               'Gemma-7b', 'CodeLlama-13b-hf',
               'StarCoder2-15b', 'CodeGEN-350M']


def nearly_Correct():
    data_list = {}


    for i in range(1, 17, 1):
        temperature = i / 10
        data_list[temperature] = select_best_complete(models=models, temperature=temperature)

    print(data_list)
    all_data_list = copy.deepcopy(data_list)
    temperature_list = data_list.keys()
    for temperature in temperature_list:
        for k in data_list[temperature].keys():
            model_data = data_list[temperature][k]
            data_list[temperature][k] = model_data['补全接近正确'] + model_data['补全完全正确']  # model_data['补全接近正确']
            all_data_list[temperature][k] = model_data['补全接近正确'] + model_data['补全接近错误'] + model_data['补全完全正确'] + model_data['补全完全错误']

    print(data_list)

    df = pd.DataFrame(data_list)
    # print(df)
    df = df.T
    print(df)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2', '#999999', '#9AC9DB', '#F7E1ED']
    df.plot(kind='bar', ax=ax, color=colors)

    ax.set_xlabel('Temperature')
    ax.set_ylabel('Nearly Right Number')
    ax.set_title('Nearly Right')
    ax.legend(title="Model")

    plt.xticks(rotation=0)
    plt.show()
    # df = df
    df_all = pd.DataFrame(all_data_list).T
    # 计算百分比
    percentage = (df / df_all * 100).round(1).astype(str) + '\%'

    df = df.astype(str).add('/') + df_all.astype(str) + '(' +percentage + ')'
    columns_map = dict(zip(models, models_name))
    df.rename(columns=columns_map, inplace=True)

    df.columns = [col.replace('_', r'\_') if isinstance(col, str) else col for col in df.columns]

    # Replace underscores in index labels if your index is of type string
    if df.index.dtype == 'object':
        df.index = df.index.str.replace('_', r'\_', regex=False)
    # Assuming 'df' is your DataFrame
    styled_df = df.style  # Here, you can chain styling options as needed

    latex_table = styled_df.to_latex(
        # column_format='lcc',
        column_format='l' + 'c' * len(df.columns),
        caption='Different Models with the Same Parameters Nearly Correct',
        label='Different Models with the Same Parameters Nearly Correct',
        position_float='centering',
        hrules=True,  # To add horizontal rules, similar to \toprule, \midrule, and \bottomrule in booktabs
    )
    print("latex:")
    print(latex_table)

if __name__ == '__main__':
    nearly_Correct()
