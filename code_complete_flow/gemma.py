import change_code
from cache_result import cache

from code_complete import openai_api_complete, openai_api_complete_and_describe, openai_api_complete_function, \
    codegen_api_complate, chatglm_complate, code_llama_complate, code_gemma_complate
from evaluation import get_complete_rq1_result
from get_dataset import get_huge_code_list, filter_huge_code_list
from models import code_line2str, HugeCode
from tools import get_code_first_line
from tools.sim import calculate_similarity_score

@cache('./cache/temp/gemma_complete')
def flow_gemma_complete(max_tokens = 200, prompt_max_tokens = 400, lcs_weight = 0.0, led_weight = 1.0, model='gemma', temperature=0.7):
    print("获取包含错误的原始代码数据")
    huge_code_list = get_huge_code_list() #type: list[HugeCode]

    print(f"对{len(huge_code_list)}条数据进行过滤")
    huge_code_list = filter_huge_code_list(huge_code_list)

    print("数据总量：", len(huge_code_list))
    # huge_code_list = huge_code_list[:200]
    # 第一条数据
    # print(huge_code_list[20].huge_content_str)
    # print("==================")
    # print(code_line2str(huge_code_list[20].huge_content_list_pre))
    # huge_code_list = huge_code_list[:10]

    for i in range(3):
        print("开始进行代码补全")
        huge_code_list = code_gemma_complate(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = i)
        print("代码补全完成")
    return

    # 对代码进行变换


    # 计算相似度
    huge_code_list = calculate_similarity_score(huge_code_list, lcs_weight = lcs_weight, led_weight = led_weight)


    print("查看补全代码")
    for huge_code in huge_code_list:
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))
        # if (complete_line == None):
        # print(f"待补全的代码[{code_line2str(huge_code.huge_content_list_pre)}]")
        # print(huge_code.complete.row_code, "=====")
        #
        # print(huge_code.complete.complete_code, "-----")
        print("补全：", complete_line)
        print("错误：", huge_line, huge_code.similarity_complete_to_huge)
        print("正确：", right_line, huge_code.similarity_complete_to_right)
        print("=====================================")

    # print("开始进行评估")
    count_result = get_complete_rq1_result(huge_code_list)
    print("RQ1: 现有的大语言模型补全的方法，能否补全出正确的代码？")
    print(count_result)
    return huge_code_list, count_result, max_tokens, prompt_max_tokens

if __name__ == '__main__':
    flow_gemma_complete()