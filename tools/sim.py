from models import HugeCode, code_line2str
from tools import get_code_first_line


def levenshtein_distance(s, t):
    """
    levenshtein distance
    :param s:
    :param t:
    :return:
    """
    m, n = len(s), len(t)
    d =[[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)
    return d[m][n]

def longest_common_subsequence(s, t):
    """
    longest common subsequence
    """

    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


def sim(s, t, lcs_weight=0, led_weight=1):
    """
    sim
    """
    if s is None:
        s = ''
    if t is None:
        t = ''
    lcs = longest_common_subsequence(s, t)
    led = levenshtein_distance(s, t)

    normalized_lcs = lcs / max(len(s), len(t))
    normalized_led = 1 - (led / max(len(s), len(t)))

    score = lcs_weight * normalized_lcs + led_weight * normalized_led
    return score



def calculate_similarity_score(huge_code_list: list[HugeCode], lcs_weight = 0, led_weight = 1) ->list[HugeCode]:
    for huge_code in huge_code_list:
        if huge_code.complete is None:
            huge_code.similarity_huge_to_right = 0
            huge_code.similarity_complete_to_huge = 0
            huge_code.similarity_complete_to_right = 0
            continue
        # print(get_code_first_line(huge_code.openai_complete_chatgpt3.complete_code))
        complete_line = get_code_first_line.get_line(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))

        huge_code.similarity_huge_to_right = sim(huge_line, right_line, lcs_weight=lcs_weight, led_weight=led_weight)
        huge_code.similarity_complete_to_huge = sim(huge_line, complete_line, lcs_weight=lcs_weight, led_weight=led_weight)
        huge_code.similarity_complete_to_right = sim(right_line, complete_line, lcs_weight=lcs_weight, led_weight=led_weight)

    return huge_code_list


def calculate_similarity_score_two(huge_code_list: list[HugeCode], lcs_weight = 0, led_weight = 1) ->list[HugeCode]:
    for huge_code in huge_code_list:
        if huge_code.complete is None:
            huge_code.similarity_huge_to_right = 0
            huge_code.similarity_complete_to_huge = 0
            huge_code.similarity_complete_to_right = 0
            continue
        # print(get_code_first_line(huge_code.openai_complete_chatgpt3.complete_code))
        complete_line = get_code_first_line.get_line_two(huge_code.complete.complete_code)
        huge_line = get_code_first_line.get_line_two(code_line2str(huge_code.huge_content_list_complete))
        right_line = get_code_first_line.get_line_two(code_line2str(huge_code.right_content_list_complete))

        huge_code.similarity_huge_to_right = sim(huge_line, right_line, lcs_weight=lcs_weight, led_weight=led_weight)
        huge_code.similarity_complete_to_huge = sim(huge_line, complete_line, lcs_weight=lcs_weight, led_weight=led_weight)
        huge_code.similarity_complete_to_right = sim(right_line, complete_line, lcs_weight=lcs_weight, led_weight=led_weight)

    return huge_code_list

if __name__ == '__main__':
    a = "long instantBefore = convertUTCToLocal(instant - 3 * DateTimeConstants.MILLIS_PER_HOUR);"
    b = "long instantBefore = instant - 3 * DateTimeConstants.MILLIS_PER_HOUR;"
    print(sim(a, b))