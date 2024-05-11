import change_code
from cache_result import cache

from code_complete import openai_api_complete, openai_api_complete_and_describe, openai_api_complete_function, \
    codegen_api_complate, chatglm_complate, code_llama_complate, code_gemma_complate, code_complate_by_huggingface_api
from code_complete.huggingface_api import check
from evaluation import get_complete_rq1_result
from get_dataset import get_huge_code_list, filter_huge_code_list
from models import code_line2str, HugeCode
from tools import get_code_first_line
from tools.sim import calculate_similarity_score, calculate_similarity_score_two


def flow_huggingface_complete_only(max_tokens = 200, prompt_max_tokens = 600, lcs_weight = 0.5, led_weight = 0.5, model='google/gemma-7b', temperature=0.7, random = 1, newpayload = {}, max_workers = 1):
    # check(model, newpayload)
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


    huge_code_list = code_complate_by_huggingface_api(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = random, newpayload = newpayload, max_workers  = max_workers)

@cache('./cache/temp/flow_huggingface_complete/{model}/{temperature}/{max_tokens}')
def flow_huggingface_complete(max_tokens = 200, prompt_max_tokens = 600, lcs_weight = 0.5, led_weight = 0.5, model='google/gemma-7b', temperature=0.7, random = 1, newpayload = {}, max_workers = 1):
    # check(model, newpayload)
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


    huge_code_list = code_complate_by_huggingface_api(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = random, newpayload = newpayload, max_workers  = max_workers)


    # 对代码进行变换


    # 计算相似度
    huge_code_list = calculate_similarity_score(huge_code_list, lcs_weight = lcs_weight, led_weight = led_weight)


    print("查看补全代码")
    for huge_code in huge_code_list:
        print(huge_code.file_name)
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
@cache('./cache/temp/flow_huggingface_complete_two/{model}/{temperature}/{max_tokens}')
def flow_huggingface_complete_two(max_tokens = 200, prompt_max_tokens = 600, lcs_weight = 0.5, led_weight = 0.5, model='google/gemma-7b', temperature=0.7, random = 1, newpayload = {}, max_workers = 1):
    # check(model, newpayload)
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


    huge_code_list = code_complate_by_huggingface_api(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = random, newpayload = newpayload, max_workers  = max_workers)


    # 对代码进行变换


    # 计算相似度
    huge_code_list = calculate_similarity_score_two(huge_code_list, lcs_weight = lcs_weight, led_weight = led_weight)


    print("查看补全代码")
    for huge_code in huge_code_list:
        print(huge_code.file_name)
        complete_line = get_code_first_line.get_line_two(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line_two(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line_two(code_line2str(huge_code.right_content_list_complete))
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
    max_workers = 1
    # flow_gemma_complete(model='google/gemma-7b', max_workers=max_workers, random=0)
    # flow_gemma_complete(model='facebook/incoder-6B', max_workers=max_workers) # 好垃圾
    # flow_huggingface_complete(model='bigscience/bloom', max_workers=max_workers)
    flow_huggingface_complete(model='THUDM/chatglm3-6b', max_workers=max_workers)

    # flow_gemma_complete(model='Salesforce/codegen-350M-multi', newpayload={"parameters":{"max_new_tokens":50}}, max_workers=max_workers) # under 3 pre-training data variants (NL, Multi, Mono) and 4 model size variants (350M, 2B, 6B, 16B).
    # flow_gemma_complete(model='Salesforce/codegen-350M-mono', newpayload={"parameters":{"max_new_tokens":20}}, max_workers=max_workers)
    # flow_gemma_complete(model='Salesforce/codegen-2B-multi', newpayload={"parameters": {"max_new_tokens": 20}}, max_workers=max_workers)
    # flow_gemma_complete(model='Salesforce/codegen-2B-mono', newpayload={"parameters": {"max_new_tokens": 20}}, max_workers=max_workers)