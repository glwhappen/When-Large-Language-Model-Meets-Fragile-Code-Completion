from code_complete.openai_completion import reduce_token_length
from get_dataset import get_huge_code_list
from models import HugeCode
from models import code_line2str
from tools import get_code_first_line

if __name__ == '__main__':
    huge_code_list:list[HugeCode] = get_huge_code_list()

    huge_code_list = huge_code_list[:5] # View the top 5 records

    for huge_code in huge_code_list:
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))

        print("Input: ", reduce_token_length(code_line2str(huge_code.huge_content_list_pre), 600))
        print("Buggy: ", huge_line)
        print("Fixed: ", right_line)
        print("=====================================")