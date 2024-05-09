import os
import yaml # pyyaml

# ConfigManager.py
# This module defines the ConfigManager class, used for managing and manipulating YAML format configuration files.
# Main functionalities include: creating configuration files, reading configurations, retrieving and updating configuration parameters.
# This is particularly useful for managing application settings and parameters, especially in experimental and development environments.


def find_project_root(current_dir):
    """
    Search upwards until finding the identification file to determine the project's root directory.
    """
    # Check if the current directory contains the identification file
    if os.path.isfile(os.path.join(current_dir, '.projectroot')):
        return current_dir
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        # Reached the root directory of the file system
        raise FileNotFoundError("Unable to find the project root directory identification file. Please create a .projectroot file in the project root directory.")
    # Recursively continue searching upwards
    return find_project_root(parent_dir)


class ConfigManager:
    """
    The ConfigManager class is used to manage YAML configuration files.
    It allows for loading, retrieving, and updating parameters in the configuration file.
    """

    def __init__(self, config_name='config.yml'):
        """
        Initialize a ConfigManager instance.

        :param config_name: The name of the configuration file.
        """

        # Absolute path of the current file
        current_file_path = os.path.abspath(__file__)

        # Path of the project root directory
        project_root = find_project_root(os.path.dirname(current_file_path))

        # Build the path for config.yml
        config_path = os.path.join(project_root, config_name)

        self.config_path = config_path
        # Check if the file exists, if not, create an empty file
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump({}, file)
        self.config = self._load_config()

    def _load_config(self):
        """
        Load the YAML configuration file.
        If the file does not exist or cannot be parsed, raise the corresponding exceptions. The configuration file is automatically created in normal cases.

        :return: The content of the configuration file.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.config_path} not found.")
        except yaml.YAMLError as exc:
            raise RuntimeError(f"Error while parsing YAML file: {exc}")

    def get_param(self, section, key, default=None):
        """
        Get the value of a parameter from the configuration file.

        :param section: The section in the configuration file (e.g., 'experiment').
        :param key: The key in the section.
        :param default: The default value to return if the key does not exist.
        :return: The value corresponding to the key, or the default value if it does not exist.
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        else:
            if default is not None:
                self.update_param(section, key, default)
                return default
            else:
                raise KeyError(f"Param '{key}' not found in section '{section}', and no default value provided.")

    def update_param(self, section, key, value):
        """
        Update a parameter in the configuration file.

        :param section: The section in the configuration file.
        :param key: The key in the section.
        :param value: The value to update.
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file, allow_unicode=True, default_flow_style=False)

if __name__ == '__main__':


    config_manager = ConfigManager("config.yml")
    config_manager._load_config()
    learning_rate = config_manager.get_param('experiment', 'learning_rate', 0.1)
    print(f"Learning Rate: {learning_rate}")

    config_manager.update_param('experiment', 'learning_rate', 0.02)
