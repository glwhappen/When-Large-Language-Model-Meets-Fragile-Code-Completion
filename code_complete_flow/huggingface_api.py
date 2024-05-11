import change_code
from cache_result import cache

from code_complete import code_complate_by_huggingface_api
from code_complete.huggingface_api import check
from evaluation import get_complete_rq1_result
from get_dataset import get_huge_code_list, filter_huge_code_list
from models import code_line2str, HugeCode
from tools import get_code_first_line
from tools.sim import calculate_similarity_score, calculate_similarity_score_two

@cache('./cache/temp/flow_huggingface_complete/{model}/{temperature}/{max_tokens}')
def flow_huggingface_complete(max_tokens = 200, prompt_max_tokens = 600, lcs_weight = 0.5, led_weight = 0.5, model='google/gemma-7b', temperature=0.7, random = 1, newpayload = {}, max_workers = 1):
    print("Getting original code data")
    huge_code_list = get_huge_code_list()  # type: list[HugeCode]

    print(f"Filtering {len(huge_code_list)} data")
    huge_code_list = filter_huge_code_list(huge_code_list)

    print("Total data:", len(huge_code_list))

    huge_code_list = code_complate_by_huggingface_api(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = random, newpayload = newpayload, max_workers  = max_workers)

    huge_code_list = calculate_similarity_score(huge_code_list, lcs_weight = lcs_weight, led_weight = led_weight)

    count_result = get_complete_rq1_result(huge_code_list)

    print(count_result)
    return huge_code_list, count_result, max_tokens, prompt_max_tokens
@cache('./cache/temp/flow_huggingface_complete_two/{model}/{temperature}/{max_tokens}')
def flow_huggingface_complete_two(max_tokens = 200, prompt_max_tokens = 600, lcs_weight = 0.5, led_weight = 0.5, model='google/gemma-7b', temperature=0.7, random = 1, newpayload = {}, max_workers = 1):
    print("Getting original code data")
    huge_code_list = get_huge_code_list()  # type: list[HugeCode]

    print(f"Filtering {len(huge_code_list)} data")
    huge_code_list = filter_huge_code_list(huge_code_list)

    print("Total data:", len(huge_code_list))

    huge_code_list = code_complate_by_huggingface_api(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature, random = random, newpayload = newpayload, max_workers  = max_workers)

    huge_code_list = calculate_similarity_score_two(huge_code_list, lcs_weight = lcs_weight, led_weight = led_weight)

    count_result = get_complete_rq1_result(huge_code_list)

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