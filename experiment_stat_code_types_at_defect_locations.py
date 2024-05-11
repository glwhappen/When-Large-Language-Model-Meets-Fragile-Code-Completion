import json

import pandas as pd

from change_code import TreeSitter
from get_dataset import get_huge_code_list, filter_huge_code_list
from models import code_line2str, HugeCode
from tools.get_code_first_line import get_line


def get_last_line_type(code):
    tree_sitter = TreeSitter(code)
    return tree_sitter.get_last_line_type()


def df_to_latex_general(df, caption="Table Caption", label="table_label"):
    """
    Convert a DataFrame to a LaTeX table string with automatic column handling.

    Parameters:
    - df: pandas DataFrame to convert.
    - caption: String for the table caption.
    - label: String for the LaTeX label.

    Returns:
    - A string containing the LaTeX table.
    """
    # Create the LaTeX table structure
    latex_str = r"\begin{table}[htp]" + "\n"
    latex_str += r"\centering" + "\n"
    latex_str += f"\caption{{{caption}}}" + "\n"
    latex_str += f"\label{{{label}}}" + " % 注意label应该紧跟caption命令之后" + "\n"

    # Determine the number of columns and their alignment
    num_columns = len(df.columns) + 1  # +1 for the index
    column_alignment = 'l' + 'c' * (num_columns - 1)  # 'l' for index, 'c' for columns

    latex_str += r"\begin{tabular}{" + column_alignment + "}" + "\n"
    latex_str += r"\toprule" + "\n"

    # Column headers
    column_headers = " & ".join(["Statement Type"] + [col.replace("_", " ").title() for col in df.columns]) + r" \\"
    latex_str += column_headers + "\n"
    latex_str += r"\midrule" + "\n"

    # Rows
    for index, row in df.iterrows():
        row_str = index.replace("_", r"\_")  # Replace underscores for LaTeX
        for col in df.columns:
            row_str += " & " + str(row[col])
        row_str += r" \\"
        latex_str += row_str + "\n"

    latex_str += r"\bottomrule" + "\n"
    latex_str += r"\end{tabular}" + "\n"
    latex_str += r"\end{table}"

    return latex_str
def get_last_line_type2(code, last_line_code):
    type_list = {
        "return_statement": {
            "count": 91
        },
        "parenthesized_expression": {
            "count": 0
        },
        "local_variable_declaration": {
            "count": 84
        },
        "expression_statement": {
            "count": 91
        },
        "new": {
            "count": 8
        },
        "if_statement": {
            "count": 115
        },
        "explicit_constructor_invocation": {
            "count": 4
        },
        "import_declaration": {
            "count": 17
        },
        "field_declaration": {
            "count": 17
        },
        "method_declaration": {
            "count": 9
        },
        "for_statement": {
            "count": 5
        },
        "enhanced_for_statement": {
            "count": 2
        },
        "throw_statement": {
            "count": 2
        }
    }
    tree_sitter = TreeSitter(code)
    return_flag = False
    # if last_line_code.find('return') != -1:
    #     return_flag = True
        # last_line_code = last_line_code.replace('return', '')

    print(last_line_code.strip())
    tree_list = tree_sitter.tree_list
    # print(tree_sitter.tree_list)
    for tree in tree_list[::-1]:
        # print(tree['text'])
        # print(tree)
        if tree['text'] == last_line_code.strip():
            # print(tree)
            return tree
    # for tree in tree_list:
    #     print("tree:", tree)

    if last_line_code.find('return') != -1:
        return {
            'type': 'return_statement'
        }
    if last_line_code.find('new') != -1:
        return {
            'type': 'new'
        }
    start_point = tree_list[-1]['start_point'][0]
    for tree in tree_list:
        if tree['start_point'][0] == start_point and tree['type'] in type_list:
            # input("捕获到一条")
            return tree

    return None
    # print(last_line_code.strip())
def main():

    huge_code_list = get_huge_code_list()  # type: list[HugeCode]

    print(f"对{len(huge_code_list)}条数据进行过滤")
    huge_code_list = filter_huge_code_list(huge_code_list)

    print("数据总量：", len(huge_code_list))
    # huge_code_list = huge_code_list[:3]
    count = 0
    type_dict = {}
    for huge_code in huge_code_list: # type: HugeCode
        # print(huge_code.huge_content_list_pre)
        # print(huge_code.huge_content_list_complete)
        code = code_line2str(huge_code.huge_content_list_pre) # 待补全代码 + 第一行错误代码组成的代码
        # print(code)
        code_huge_line = code + get_line(code_line2str(huge_code.huge_content_list_complete))

        code_right_line = code + get_line(code_line2str(huge_code.right_content_list_complete))

        # print("len code", len(huge_code.huge_content_list_pre))
        ans_huge = get_last_line_type(code_huge_line)
        ans_right = get_last_line_type(code_right_line)


        huge_type = ans_huge['type']
        right_type = ans_right['type']
        if huge_type in type_dict:
            type_dict[huge_type]['huge_count'] += 1
            # type_dict[type]['tree_node_list'].append(ans)
        else:
            type_dict[huge_type] = {
                'huge_count': 1,
                'right_count': 0,
            }

        if right_type in type_dict:
            type_dict[right_type]['right_count'] += 1
            # type_dict[type]['tree_node_list'].append(ans)
        else:
            type_dict[right_type] = {
                'huge_count': 0,
                'right_count': 1,
            }
    print(json.dumps(type_dict))
    df = pd.DataFrame(type_dict).T
    df = df.sort_values(by=['huge_count', 'right_count'], ascending=False)
    df = df.rename(columns={'huge_count': 'Worong Count', 'right_count': 'Correct Count'})
    df.index.name = 'Statement Type'
    # df = df.reset_index(drop=True)
    print(df)
    # print(df_to_latex_general(df, "Comparative Statistics of Error Types in Wrong Code vs. Correct Code", "defects4j_type"))

    # Assuming 'df' is your DataFrame
    # Replace underscores in column names
    df.columns = [col.replace('_', r'\_') for col in df.columns]

    # Replace underscores in index labels if your index is of type string
    if df.index.dtype == 'object':
        df.index = df.index.str.replace('_', r'\_', regex=False)
    # Assuming 'df' is your DataFrame
    styled_df = df.style  # Here, you can chain styling options as needed

    latex_table = styled_df.to_latex(
        # column_format='lcc',
        column_format='l' + 'c' * len(df.columns),
        caption='Comparative Statistics of Error Types in Wrong Code vs. Correct Code',
        label='defects4j_type',
        position_float='centering',
        hrules=True,  # To add horizontal rules, similar to \toprule, \midrule, and \bottomrule in booktabs
    )
    print("latex:")
    print(latex_table)

if __name__ == '__main__':
    main()