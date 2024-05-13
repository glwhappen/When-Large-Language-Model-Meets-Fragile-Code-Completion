import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import tools
from code_complete_flow import flow_openai_api_complete
from tools.experiment import save_csv, save_figure


def compare_gpt3_temperature():
    count_result_list = []
    descriptions = []
    max_tokens = []
    prompt_max_tokens = []
    temperature_list = []


    for i in range(1, 20):
        lcs_wight = 0.5
        temperature = i / 10
        print(f"run temperature {temperature}")
        _, count_result, max_token, prompt_max_token = flow_openai_api_complete(max_tokens=200, prompt_max_tokens=600,
                                                                                lcs_weight=lcs_wight, led_weight=1-lcs_wight, temperature=temperature)
        count_result_list.append(count_result.to_dict())
        descriptions.append(f"openai api complete lcs_weight={lcs_wight}, led_weight={1 - lcs_wight}, temperature={temperature}")

        max_tokens.append(max_token)
        prompt_max_tokens.append(prompt_max_token)
        temperature_list.append(temperature)


    df = pd.DataFrame(count_result_list)

    df['description'] = descriptions
    df['temperature'] = temperature_list
    df.drop('总量', axis=1, inplace=True)

    print(df)

    file_name = os.path.basename(__file__).rsplit('.', 1)[0]

    save_csv(df, file_name)

    data = df

    temperatures = data['temperature']
    nearly_correct = data['补全接近正确']
    nearly_wrong = data['补全接近错误']
    completely_correct = data['补全完全正确']
    completely_wrong = data['补全完全错误']
    non_compliant = data['补全不符合']
    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2', '#999999', '#9AC9DB', '#F7E1ED']
    plt.figure(figsize=(10, 6))
    linewidth = 3
    markersize = 6
    fontsize = 13

    plt.plot(temperatures, nearly_correct, label="Nearly Correct", marker='o', color=colors[0], linewidth=linewidth, markersize=markersize)
    plt.plot(temperatures, nearly_wrong, label="Nearly Faulty", color=colors[1], linewidth=linewidth, markersize=markersize)
    plt.plot(temperatures, completely_correct, label="Completely Correct", marker='s', color=colors[2], linewidth=linewidth, markersize=markersize)
    plt.plot(temperatures, completely_wrong, label="Completely Faulty", marker='*', color=colors[3], linewidth=linewidth, markersize=markersize+2)
    plt.plot(temperatures, non_compliant, label="Non-compliant", marker='^', color=colors[4], linewidth=linewidth, markersize=markersize)




    plt.xlabel('Temperature', fontsize=fontsize)
    plt.ylabel('Number of Instances', fontsize=fontsize)
    plt.legend(fontsize=fontsize)
    plt.grid(False)
    plt.tick_params(axis='both', labelsize=fontsize)


    plt.xticks(np.arange(0, 2.1, 0.2))  # Setting x-axis ticks to increment by 0.1

    pdf_file_path = f"./experimental results/temperature_line_graph.pdf"
    plt.savefig(pdf_file_path, format='pdf')

    plt.show()



if __name__ == '__main__':

    while True:
        try:
            compare_gpt3_temperature()
            break
        except:
            print("An error occurred, let's try again.")

