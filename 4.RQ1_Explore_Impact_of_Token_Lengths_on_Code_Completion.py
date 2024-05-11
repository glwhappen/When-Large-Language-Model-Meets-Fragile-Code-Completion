import os

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


    for prompt_max_tokens in [1000, 800, 700, 650, 600, 550, 500, 400, 300, 200]:
        _, count_result, max_token, prompt_max_token = flow_openai_api_complete(max_tokens=200, prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=0.5, led_weight=0.5)
        count_result_list.append(count_result.to_dict())
        descriptions.append(f"openai api进行补全 prompt_max_tokens={prompt_max_tokens}")
        temperature_list.append(prompt_max_token)

    df = pd.DataFrame(count_result_list)

    df['description'] = descriptions
    df['token'] = temperature_list
    df.drop('总量', axis=1, inplace=True)


    print(df)


    file_name = os.path.basename(__file__).rsplit('.', 1)[0]

    save_csv(df, file_name)

    # Extracting values for plotting
    tokens = df['token']
    nearly_correct = df['补全接近正确']
    nearly_wrong = df['补全接近错误']
    completely_correct = df['补全完全正确']
    completely_wrong = df['补全完全错误']
    non_compliant = df['补全不符合']

    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2', '#999999', '#9AC9DB', '#F7E1ED']

    plt.figure(figsize=(10, 6))
    linewidth = 3
    markersize = 6
    fontsize = None

    plt.plot(tokens, nearly_correct, label="Nearly Correct", marker='o', color=colors[0], linewidth=linewidth,
             markersize=markersize)
    plt.plot(tokens, nearly_wrong, label="Nearly Faulty", color=colors[1], linewidth=linewidth, markersize=markersize)
    plt.plot(tokens, completely_correct, label="Completely Correct", marker='s', color=colors[2], linewidth=linewidth,
             markersize=markersize)
    plt.plot(tokens, completely_wrong, label="Completely Faulty", marker='*', color=colors[3], linewidth=linewidth,
             markersize=markersize + 2)
    plt.plot(tokens, non_compliant, label="Non-compliant", marker='^', color=colors[4], linewidth=linewidth,
             markersize=markersize)

    # Adding a vertical line at token length of 600
    plt.axvline(x=600, color='grey', linestyle='--')

    # Adjusting the annotation for token length of 600 with an arrow
    plt.annotate('Token Length=600', xy=(600, 60), xytext=(553, 60 + 15),
                 arrowprops=dict(color=colors[6], shrink=0.05),
                 fontsize=10, color='dimgrey')

    # Labeling the plot
    # plt.title('Impact of Token Length on Code Completion')
    plt.xlabel('Token Length')
    plt.ylabel('Number of Instances')
    plt.legend()
    plt.grid(False)


    pdf_file_path = f"./experimental results/token_len.pdf"
    plt.savefig(pdf_file_path, format='pdf')

    # Display the plot
    plt.show()


if __name__ == '__main__':
    compare_gpt3_temperature()