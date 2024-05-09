from change_code.TreeSitter import TreeSitter
from models import HugeCode, code_line2str, code_str2line
from tools import get_code_first_line


def change_insert_print(huge_code_list: list[HugeCode]) -> list[HugeCode]:
    for huge_code in huge_code_list:
        tcode = code_line2str(huge_code.huge_content_list_pre)
        # tcode += get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        tree_sitter = TreeSitter(tcode)

        huge_code.huge_content_list_pre = code_str2line(tree_sitter.insert_print_local_variable())


    return huge_code_list


def change_str(huge_code_list: list[HugeCode]) -> list[HugeCode]:
    for huge_code in huge_code_list:
        tcode = code_line2str(huge_code.huge_content_list_pre)

        tree_sitter = TreeSitter(tcode)

        huge_code.huge_content_list_pre = code_str2line(tree_sitter.replace_strings_in_code(tcode))

    return huge_code_list

def change_args(huge_code_list: list[HugeCode]) -> list[HugeCode]:
    for huge_code in huge_code_list:
        _change_args(huge_code)
    return huge_code_list

def _change_args(huge_code: HugeCode):

    # 1. Get the result of equivalent replacement of the original code with the error line added.
    # 2. Get the result of the original code with the correct line added.

    tcode = code_line2str(huge_code.huge_content_list_pre)
    tcode += get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
    tree_sitter = TreeSitter(tcode)
    # last_line = tree_sitter.change_args().strip().split('\n')[-1]

    tcode = code_line2str(huge_code.huge_content_list_pre)
    tree_sitter = TreeSitter(tcode)
    change_args_pre_code = tree_sitter.change_args()
    print(change_args_pre_code)
    input("pause")
    huge_code.huge_content_list_pre = code_str2line(change_args_pre_code)

