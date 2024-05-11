import os

from cache_result import cache
from change_code import TreeSitter

from models import HugeCode, code_line2str
from get_dataset import read as readUtil, utils
from tools.ConfigManager import ConfigManager


@cache('cache/dataset')
def get_huge_code_list() -> list[HugeCode]:
    """
    Get the raw code data containing errors, and split the code into incomplete code and complete code,
    also including correct code.
    :return: list[HugeCode] A HugeCode object represents one piece of data.
    """
    project_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the current file is located, i.e., the project path.
    config_manager = ConfigManager()
    dataset_path = config_manager.get_param('config', 'dataset_path', 'C:\\happen\\dataset\\completeOutput')

    version_dirs = utils.get_completeOutput_version_dirs(
        dataset_path)  # ['C:\\happen\\dataset\\completeOutput\\Chart\\10b']

    print(len(version_dirs))

    all_huge_code_list = []

    for dir in version_dirs:
        huge_code_list = readUtil.get_and_split_complete_code(dir=dir)  # get code
        for huge_code in huge_code_list:
            huge_code.version_dir = dir
            all_huge_code_list.append(huge_code)
    # return all_huge_code_list[:100]
    return all_huge_code_list


@cache('cache/dataset')
def filter_huge_code_list(huge_code_list: list[HugeCode]) -> list[HugeCode]:
    """
    Filter out data that does not meet the conditions.
    :param huge_code_list: List of HugeCode objects to be filtered.
    :return: Filtered list of HugeCode objects.
    """
    result: list[HugeCode] = []
    for huge_code in huge_code_list:
        if (code_line2str(huge_code.huge_content_list_pre) == code_line2str(
                huge_code.right_content_list_pre)):
            result.append(huge_code)
        else:
            print("filted a data")

    return result


def get_function_from_code(code, code_pre) -> str:
    """
    Get the incomplete function from the code.
    :param code: The complete code.
    :param code_pre: The preceding code.
    :return: Incomplete function extracted from the code.
    """
    code_len = len(code.split('\n'))  # code length
    code_pre_len = len(code_pre.split('\n'))  # length of code pre
    print("code_len", code_len)
    print("code_pre_len", code_pre_len)
    err_len = code_pre_len + 1  # 错误行
    print("err_len", err_len)
    treeSitter = TreeSitter(code)
    function_code, start_line, end_line  = treeSitter.find_function(err_len)
    print("function_code:", function_code)
    if function_code == None:
        return ""
    function_len = len(function_code.split('\n'))
    function_err_len = err_len - start_line
    print("function_len", function_len)
    print("err_len", err_len)
    print("code_len", code_len)
    print("start_line", start_line)
    print("end_line", end_line)
    print("function_err_len", function_err_len)
    # print(function_code.split('\n')[: function_err_len + 1])

    result_code = function_code.split('\n')[: function_err_len - 2]
    if result_code and result_code[0].startswith('@'):
        result_code = result_code[1:]
    # huge_code.function_code_str = function_code
    return '\n'.join(result_code)
    # print(huge_code.function_code_pre_str + '\n' + code_line2str(huge_code.huge_content_list_complete))
    # return huge_code

    # return ''


def add_function_huge_code(huge_code: HugeCode) -> HugeCode:
    code_len = len(huge_code.huge_content_list)  # code length
    # print(len(huge_code_list[0].huge_content_list_pre))
    # print(code_line2str(huge_code_list[0].huge_content_list_pre))
    code_pre_len = len(huge_code.huge_content_list_pre)
    err_len = code_pre_len + 1  # fault line
    treeSitter = TreeSitter(code_line2str(huge_code.huge_content_list))
    function_code, start_line, end_line = treeSitter.find_function(err_len)
    # print(function_code)
    if function_code == None:
        return huge_code
    function_len = len(function_code.split('\n'))
    function_err_len = err_len - (code_len - function_len)
    # print("function_len", function_len)
    # print("err_len", err_len)
    # print("code_len", code_len)
    # print(function_err_len)
    # print(function_code.split('\n')[: function_err_len + 1])

    huge_code.function_code_str = function_code
    huge_code.function_code_pre_str = ''.join(function_code.split('\n')[: function_err_len + 1])
    # print(huge_code.function_code_pre_str + '\n' + code_line2str(huge_code.huge_content_list_complete))
    return huge_code


def add_function_code(huge_code_list: list[HugeCode]) -> list[HugeCode]:
    """
    Return the code of the function where the error lines are located.
    Fields: function_code_str, function_code_pre_str
    :param huge_code_list: List of HugeCode objects.
    :return: List of HugeCode objects with added function code.
    """
    # huge_code_list = get_huge_code_list() #type: # list[HugeCode]
    error_len = 0
    for huge_code in huge_code_list:
        huge_code = add_function_huge_code(huge_code)

    return huge_code_list


if __name__ == '__main__':
    # huge_code_list = get_huge_code_list()
    # print(len(huge_code_list))
    code1 = ""


    data = "2023-12-28-01-35-00"
    with open(f"../log/{data}_all.txt", "r", encoding="utf-8") as f:
        code1 = f.read()

    code1_pre = ""

    with open(f"../log/{data}.txt", "r", encoding="utf-8") as f:
        code1_pre = f.read()

    print(get_function_from_code(code1, code1_pre))
