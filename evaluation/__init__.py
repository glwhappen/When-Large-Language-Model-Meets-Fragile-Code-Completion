from models import CompleteResult, code_line2str, HugeCode

def _get_complete_rq1_result(huge_code_list: list[HugeCode]) -> CompleteResult:
    from tools import get_code_first_line
    from tools.sim import sim

    count = CompleteResult()


    for huge_code in huge_code_list:
        # print(get_code_first_line(huge_code.openai_complete_chatgpt3.complete_code))
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))

        if sim(huge_line, complete_line) == 1:
            count.wrong += 1
        elif sim(right_line, complete_line) == 1:
            count.right += 1
        if sim(huge_line, complete_line) > sim(right_line, complete_line):
            count.sim_right += 1
        else:
            count.sim_wrong += 1

        count.total += 1

    return count


def get_complete_rq1_result(huge_code_list: list[HugeCode]) -> CompleteResult:
    count = CompleteResult()


    for huge_code in huge_code_list:
        count.total += 1
        if huge_code.similarity_complete_to_huge < 0.4 and huge_code.similarity_complete_to_right < 0.4:
            count.error += 1
            continue
        if huge_code.similarity_complete_to_huge > 0.99:
            count.wrong += 1
        elif huge_code.similarity_complete_to_right > 0.99:
            count.right += 1

        elif huge_code.similarity_complete_to_right > huge_code.similarity_complete_to_huge:
            count.sim_right += 1
        else:
            count.sim_wrong += 1

    return count