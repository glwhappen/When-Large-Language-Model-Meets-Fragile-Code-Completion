import threading

from retrying import retry

from get_dataset import get_huge_code_list, filter_huge_code_list, get_function_from_code  # 获取数据


from models import HugeCode, code_line2str
from tools import get_code_first_line
from tools.code_format import test_remove_copy_code

def openai_api_complete(huge_code_list: list[HugeCode], model='gpt-3.5-turbo-instruct', max_tokens=100, prompt_max_tokens=300, temperature=0.7) -> list[HugeCode]:
    """
    openai_api_complete
    :return:
    """

    print("openai_api_complete")
    from code_complete.openai_completion import complete

    @retry(stop_max_attempt_number=5, wait_random_min=3000, wait_random_max=5000)
    def process_code(huge_code):
        try:
            print(huge_code.file_name)
            complete_result = complete(code_line2str(huge_code.huge_content_list_pre), max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, temperature=temperature)
            complete_result.complete_code = test_remove_copy_code(complete_result.complete_code)
            huge_code.complete = complete_result
        except Exception as e:
            print(f"Error processing {huge_code.file_name}: {e}")
            raise e  # Rethrow the exception to handle it in the caller or further up the stack



    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_code, huge_code_list)

    return huge_code_list


lock = threading.Lock()
current_count = 0
max_count = 0


def code_complate_by_huggingface_api(huge_code_list: list[HugeCode], model='google/gemma-7b', max_tokens=100, prompt_max_tokens=300, temperature=0.7, random = 1, newpayload={}, max_workers=3) -> list[HugeCode]:
    """
    使用openai的接口进行代码补全
    :return:
    """

    print("使用openai api对所有代码进行补全")
    from code_complete.huggingface_api import complete


    @retry(stop_max_attempt_number=5, wait_random_min=3000, wait_random_max=5000)
    def process_code(huge_code):
        global current_count, max_count
        # 在任务开始时增加计数器
        with lock:
            current_count += 1
            max_count = max(max_count, current_count)

        print(huge_code.file_name)
        complete_result = complete(code_line2str(huge_code.huge_content_list_pre), max_tokens=max_tokens, prompt_max_tokens=prompt_max_tokens, model=model, random = random, newpayload = newpayload, temperature=temperature)
        complete_result.complete_code = test_remove_copy_code(complete_result.complete_code)
        huge_code.complete = complete_result
        print(huge_code.complete)

        # 在任务结束时减少计数器
        with lock:
            current_count -= 1
            print(max_count, current_count)

    # 使用ThreadPoolExecutor并行处理代码
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_code, huge_code_list) # 使用map函数将任务分配到各个线程中

    return huge_code_list


import concurrent.futures


if __name__ == '__main__':
    print("Getting original code data")
    huge_code_list = get_huge_code_list()  # type: list[HugeCode]

    print(f"Filtering {len(huge_code_list)} data")
    huge_code_list = filter_huge_code_list(huge_code_list)


    huge_code_list = huge_code_list[:200]
    print("Total data:", len(huge_code_list))
    print("Start code completion")


    huge_code_list = openai_api_complete(huge_code_list)
    print("Code completion completed")

    print("Viewing completed code")
    for huge_code in huge_code_list:
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))
        # if (complete_line == None):
        print(f"Original code to be completed, last 5 lines:\n{code_line2str(huge_code.huge_content_list_pre[-5:])}")
        # print(huge_code.complete.row_code, "=====")

        print("Completed code:\n", huge_code.complete.complete_code)
        print("Process the result into 1 line, then compare this line of code")
        print("Completion:", complete_line)
        print("Error:", huge_line)
        print("Correct:", right_line)
        print("=====================================")
