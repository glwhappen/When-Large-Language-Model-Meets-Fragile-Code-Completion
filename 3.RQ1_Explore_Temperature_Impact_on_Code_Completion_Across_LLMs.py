import os

import pandas as pd
from matplotlib import pyplot as plt

from tools.experiment import save_csv, save_figure
from impact_of_temperature_parameters_on_code_completion import compare_temperature

models = ['openai/gpt-3.5-turbo-instruct',
          'google/gemma-7b', 'codellama/CodeLlama-13b-hf',
          'bigcode/starcoder2-15b', 'Salesforce/codegen-350M-multi']

models_name = ['OpenAI-GPT3.5',
               'Gemma-7b', 'CodeLlama-13b-hf',
               'StarCoder2-15b', 'CodeGEN-350M']

columns_map = dict(zip(models, models_name))
def main():
    max_workers = 10
    result = {}
    temperature_list = [i / 10 for i in range(1, 17)]
    models = ['openai/gpt-3.5-turbo-instruct',
              'google/gemma-7b', 'codellama/CodeLlama-13b-hf',
              'bigcode/starcoder2-15b', 'Salesforce/codegen-350M-multi']
    type_list = ['补全接近正确', '补全接近错误', '补全完全正确', '补全完全错误']
    for type in type_list:
        for model in models:
            count_result_list, descriptions = compare_temperature(model=model, max_workers=max_workers)
            for count_result, description, temperature in zip(count_result_list, descriptions, temperature_list):
                print(count_result, description, temperature)
                if type in result:
                    result[type].append((model, temperature, (count_result[type])))
                else:
                    result[type] = [(model, temperature, (count_result[type]))]

    df = {}
    pivot_df = {}
    for type in type_list:
        df[type] = pd.DataFrame(result[type], columns=['Model', 'Temperature', 'Value'])
        pivot_df[type] = df[type].pivot(index='Model', columns='Temperature', values='Value')


    plt.figure(figsize=(7, 4))

    fig, axs = plt.subplots(2, 2, figsize=(16, 12), sharex=True, sharey=True) #  , gridspec_kw={'left': 0.1}
    plt.style.use('seaborn-white')
    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2', '#999999']
    line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))] # (0, (3, 10, 1, 10)) for line length 3, gap 10, line length 1, gap 10
    fontsize=20

    def plot_data(ax, data, title):
        for (model, row), color, line_style in zip(data.iterrows(), colors, line_styles):
            ax.plot(row.index, row.values, label=columns_map[model], color=color, linestyle=line_style, linewidth=5)
        ax.set_title(title, fontsize=fontsize+2)
        ax.tick_params(axis='both', labelsize=fontsize)
        if title == 'Completely Faulty':
            ax.legend(fontsize=fontsize)
        # ax.set_ylabel('% of Total')
        # ax.set_xlabel('Temperature')
        ax.grid(False)

    plot_data(axs[0, 0], pivot_df['补全接近正确'] / 546 * 100, 'Nearly Correct')
    plot_data(axs[0, 1], pivot_df['补全接近错误'] / 546 * 100, 'Nearly Faulty')
    plot_data(axs[1, 0], pivot_df['补全完全正确'] / 546 * 100, 'Completely Correct')
    plot_data(axs[1, 1], pivot_df['补全完全错误'] / 546 * 100, 'Completely Faulty')

    plt.tight_layout(pad=5)
    fig.text(0.5, 0.02, 'Temperature', ha='center', va='center', fontsize=fontsize)

    fig.text(0.03, 0.5, '% of Total', ha='center', va='center', rotation='vertical', fontsize=fontsize)

    file_name = os.path.basename(__file__).split('.')[0]
    plt.grid(False)
    plt.tight_layout()
    plt.subplots_adjust(left=0.07, bottom=0.07)  # Increase the left blank area
    # fig.adjust(left=0.5)  # If 0.15 is the left boundary space you need, you can adjust this value according to the actual situation

    save_figure(plt, file_name)



    plt.show()

    # Calculate the total scores for "good" completions and "bad" completions

    total_good = pivot_df['补全接近正确']
    total_bad = pivot_df['补全接近错误']

    # Calculate advantage scores: the difference between good completions and bad completions
    advantage_scores = total_good - total_bad
    # Calculate the average advantage score for each temperature and find the temperature with the highest average score
    optimal_temperature = advantage_scores.mean().idxmax()

    print(optimal_temperature)


if __name__ == '__main__':
    main()
