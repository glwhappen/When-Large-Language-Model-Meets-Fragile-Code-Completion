import pandas as pd

from cache_result import cache

from code_complete_flow.huggingface_api import flow_huggingface_complete

from models import code_line2str
from tools import get_code_first_line

import json

from experiment_stat_code_types_at_defect_locations import get_last_line_type


@cache("cache/temp/code_type/{model}/5")
def select_best_complete(lcs_wight = 0.5, led_wight = 0.5, model="google/gemma-7b", start=1, end=3, newpayload={}, max_tokens=50,prompt_max_tokens=600, temperature = 0.4, max_workers=3, random=1):

        huge_code_list, count_result, max_token, prompt_max_token = flow_huggingface_complete(max_tokens=max_tokens,
                                                                                             prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=lcs_wight, led_weight=1-lcs_wight, model=model, random=1, newpayload={}, temperature=temperature, max_workers=max_workers)
        print(count_result.to_dict())
        right_line_type_dict = {

        }
        complete_code_type_dict = {

        }
        print(len(huge_code_list))

        for huge_code in huge_code_list:
            key = huge_code.version_dir + huge_code.file_name
            code = code_line2str(huge_code.huge_content_list_pre)  # 待补全代码 + 第一行错误代码组成的代码
            huge_line = get_code_first_line.get_line(code_line2str(huge_code.huge_content_list_complete))
            right_line = get_code_first_line.get_line(code_line2str(huge_code.right_content_list_complete))

            complete_code = get_code_first_line.get_line(huge_code.complete.complete_code)



            if huge_code.similarity_complete_to_huge > huge_code.similarity_complete_to_right >= 0.4: # or huge_code.similarity_complete_to_right > 0.99:

                huge_code_type = get_last_line_type(code + huge_line)['type']
                right_line_type = get_last_line_type(code + right_line)['type']
                complete_code_type = get_last_line_type(code + complete_code)['type']
                model_name = model
                # if model_name.find('/') != -1:
                #     model_name = model_name.split('/')[-1]
                count_name = f'{model_name}'
                if right_line_type in right_line_type_dict:
                    print(right_line_type_dict[right_line_type])
                    right_line_type_dict[right_line_type][count_name]['wrong'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    right_line_type_dict[right_line_type] = {
                        count_name: {
                            'wrong': 1,
                            'correct': 0,
                            'not': 0,
                        },
                        # 'tree_node_list': [ans]
                    }

                if complete_code_type in complete_code_type_dict:
                    complete_code_type_dict[complete_code_type][count_name]['wrong'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    complete_code_type_dict[complete_code_type] = {
                        count_name: {
                            'wrong': 1,
                            'correct': 0,
                            'not': 0,
                        },
                        # 'tree_node_list': [ans]
                    }

            elif huge_code.similarity_complete_to_right > huge_code.similarity_complete_to_huge >= 0.4:

                huge_code_type = get_last_line_type(code + huge_line)['type']
                right_line_type = get_last_line_type(code + right_line)['type']
                complete_code_type = get_last_line_type(code + complete_code)['type']
                model_name = model
                # if model_name.find('/') != -1:
                #     model_name = model_name.split('/')[-1]
                count_name = f'{model_name}'
                if right_line_type in right_line_type_dict:
                    right_line_type_dict[right_line_type][count_name]['correct'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    right_line_type_dict[right_line_type] = {
                        count_name: {
                            'correct': 1,
                            'wrong': 0,
                            'not': 0,
                        },
                        # 'tree_node_list': [ans]
                    }

                if complete_code_type in complete_code_type_dict:
                    complete_code_type_dict[complete_code_type][count_name]['correct'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    complete_code_type_dict[complete_code_type] = {
                        count_name: {
                            'correct': 1,
                            'wrong': 0,
                            'not': 0,
                        },
                        # 'tree_node_list': [ans]
                    }

            else:

                huge_code_type = get_last_line_type(code + huge_line)['type']
                right_line_type = get_last_line_type(code + right_line)['type']
                complete_code_type = get_last_line_type(code + str(complete_code))['type']
                model_name = model
                # if model_name.find('/') != -1:
                #     model_name = model_name.split('/')[-1]
                count_name = f'{model_name}'
                if right_line_type in right_line_type_dict:
                    right_line_type_dict[right_line_type][count_name]['not'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    right_line_type_dict[right_line_type] = {
                        count_name: {
                            'correct': 0,
                            'wrong': 0,
                            'not': 1,
                        },
                        # 'tree_node_list': [ans]
                    }

                if complete_code_type in complete_code_type_dict:
                    complete_code_type_dict[complete_code_type][count_name]['not'] += 1
                    # type_dict[type]['tree_node_list'].append(ans)
                else:
                    complete_code_type_dict[complete_code_type] = {
                        count_name: {
                            'correct': 0,
                            'wrong': 0,
                            'not': 1,
                        },
                        # 'tree_node_list': [ans]
                    }



        print(json.dumps(right_line_type_dict))
        return right_line_type_dict, count_result

models = ['openai/gpt-3.5-turbo-instruct',
          'google/gemma-7b', 'codellama/CodeLlama-13b-hf',
          'bigcode/starcoder2-15b', 'Salesforce/codegen-350M-multi']

models_name = ['OpenAI-GPT3.5',
               'Gemma-7b', 'CodeLlama-13b-hf',
               'StarCoder2-15b', 'CodeGEN-350M']

if __name__ == '__main__':



    data_list = []
    for model in models:

        data, count_result = select_best_complete(model=model)
        data_list.append((data, count_result))

    combined_df = pd.DataFrame()

    # Iterate through the list to transform and combine data
    for item, count_results in data_list:
        print(count_results.to_dict()['补全接近正确'] + count_results.to_dict()['补全接近错误'])
        for statement_type, counts in item.items():
            for model, count in counts.items():
                combined_df = pd.concat([combined_df, pd.DataFrame.from_records(
                    [{"Statement Type": statement_type, "Model": model, "sign": f"{count['correct']}/{count['wrong']}/{count['not']}", "correct": count['correct'],"wrong": count['wrong'],"not": count['not'], "all": count['correct'] + count['wrong']}])], ignore_index=True)
    print(combined_df)
    # Pivot the DataFrame to get models as columns
    # result_df = combined_df.pivot(index='Statement Type', columns='Model', values='Count').fillna(0).astype(int)
    df = combined_df.pivot(index='Model', columns='Statement Type', values='sign')
    # 错误的和正确的占比
    # result_df = result_df.drop(result_df.index[1])
    print(df)
    df_wrong = combined_df.pivot(index='Model', columns='Statement Type', values='wrong').fillna(0).astype(int)
    df_not = combined_df.pivot(index='Model', columns='Statement Type', values='not').fillna(0).astype(int)
    df_all = combined_df.pivot(index='Model', columns='Statement Type', values='all').fillna(0).astype(int)

    # result_df = result_df.drop(result_df.index[1])
    print(df_all)

    df = df.T
    df_all = df_all.T
    print(df)
    print(df.columns)

    columns_map = dict(zip(models, models_name))
    df.rename(columns=columns_map, inplace=True)
    print(df)
    type = ['return_statement', 'local_variable_declaration', 'expression_statement',
                                        'if_statement', 'import_declaration', 'field_declaration',
                                        'while_statement', 'method_invocation',
                                        'method_declaration', 'for', 'throw_statement', 'identifier', 'other']
    type_name = ['Return Statement', 'Variable Declaration', 'Expression Statement',
                                        'If Statement', 'Import Declaration', 'Field Declaration',
                                        'While Statement', 'Method Declaration',
                                        'Method Invocation', 'For Statement', 'Throw Statement', 'Identifier', 'Other']
    type_map = dict(zip(type, type_name))
    print(df)
    print(df.index)
    df.index = df.index.map(type_map)


    df.columns = [col.replace('_', r'\_') if isinstance(col, str) else col for col in df.columns]



    # Replace underscores in index labels if your index is of type string
    if df.index.dtype == 'object':
        df.index = df.index.str.replace('_', r'\_', regex=False)
    # Assuming 'df' is your DataFrame
    styled_df = df.style  # Here, you can chain styling options as needed

    latex_table = styled_df.to_latex(
        # column_format='lcc',
        column_format='l' + 'c' * len(df.columns),
        caption='The code types of the fixed code that correspond to the completion results from different models',
        label='The code types of the fixed code that correspond to the completion results from different models',
        position_float='centering',
        hrules=True,  # To add horizontal rules, similar to \toprule, \midrule, and \bottomrule in booktabs
    )
    print("latex:")
    print(latex_table)
