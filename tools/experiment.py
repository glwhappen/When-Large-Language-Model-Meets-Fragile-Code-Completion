import os

import tools


def save_csv(df, file_name):
    project_root = tools.find_project_root()
    base_path = os.path.join(project_root, 'experimental results')

    os.makedirs(base_path, exist_ok=True)

    df.to_csv(os.path.join(base_path, f'{file_name}.csv'))
    df.to_markdown(os.path.join(base_path, f'{file_name}.md'))

def save_figure(plt, file_name):
    project_root = tools.find_project_root()
    base_path = os.path.join(project_root, 'experimental results')

    os.makedirs(base_path, exist_ok=True)

    plt.savefig(os.path.join(base_path, f'{file_name}.png'), dpi=300)

    plt.savefig(os.path.join(base_path, f'{file_name}.pdf'), format='pdf')