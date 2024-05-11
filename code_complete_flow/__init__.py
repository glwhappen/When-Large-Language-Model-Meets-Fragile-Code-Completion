import change_code
from cache_result import cache

from code_complete import openai_api_complete
from evaluation import get_complete_rq1_result
from get_dataset import get_huge_code_list, filter_huge_code_list
from models import code_line2str, HugeCode
from tools import get_code_first_line
from tools.sim import calculate_similarity_score


@cache('./cache/temp/openai_api_complete')
def flow_openai_api_complete(max_tokens=200, prompt_max_tokens=400, lcs_weight=0.0, led_weight=1.0, model='gpt-3.5-turbo-instruct', temperature=0.7):
    print("Getting original code data")
    huge_code_list = get_huge_code_list()  # type: list[HugeCode]

    print(f"Filtering {len(huge_code_list)} data")
    huge_code_list = filter_huge_code_list(huge_code_list)

    print("Total data:", len(huge_code_list))
    # huge_code_list = huge_code_list[:50]
    # First data
    # print(huge_code_list[20].huge_content_str)
    # print("==================")
    # print(code_line2str(huge_code_list[20].huge_content_list_pre))
    # huge_code_list = huge_code_list[:10]

    print("Start code completion")
    huge_code_list = openai_api_complete(huge_code_list, max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature)
    print("Code completion completed")

    # Transform the code

    # Calculate similarity
    huge_code_list = calculate_similarity_score(huge_code_list, lcs_weight=lcs_weight, led_weight=led_weight)

    print("Viewing completed code")
    for huge_code in huge_code_list:
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))
        # if (complete_line == None):
        # print(f"Original code to be completed[{code_line2str(huge_code.huge_content_list_pre)}]")
        # print(huge_code.complete.row_code, "=====")
        #
        # print(huge_code.complete.complete_code, "-----")
        print("Completion:", complete_line)
        print("Error:", huge_line, huge_code.similarity_complete_to_huge)
        print("Correct:", right_line, huge_code.similarity_complete_to_right)
        print("=====================================")

    # print("Starting evaluation")
    count_result = get_complete_rq1_result(huge_code_list)

    print(count_result)
    return huge_code_list, count_result, max_tokens, prompt_max_tokens






if __name__ == '__main__':
    flow_openai_api_complete()
    # flow_chatglm_complete()