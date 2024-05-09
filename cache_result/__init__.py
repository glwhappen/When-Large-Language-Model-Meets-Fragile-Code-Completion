import os
import pickle
import hashlib
import inspect
import re
import time

from colorama import Fore, Back, Style

def find_project_root(current_dir):
    """
    Search upwards until the marker file is found, identifying the project's root directory.
    """
    # Check if the current directory contains the marker file
    if os.path.isfile(os.path.join(current_dir, '.projectroot')):
        return current_dir
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        # Reached the root of the file system
        raise FileNotFoundError("Unable to find the project root marker file. Please create a '.projectroot' file in the project's root directory.")
    # Recursively continue searching upwards
    return find_project_root(parent_dir)

def remove_unused_code(source_code):
    """
    Remove unused code from the given source code.
    """
    # Remove single-line comments
    source_code = re.sub(r'#.*$', "", source_code, flags=re.MULTILINE)
    # Remove multi-line comments
    source_code = re.sub(r'""".*?"""', "", source_code, flags=re.MULTILINE | re.DOTALL)
    # Remove print statements
    source_code = re.sub(r'print\(.*\)', "", source_code)
    # Remove decorators
    source_code = re.sub(r'@.*\(.*\)', '', source_code)
    return source_code


def cache(cache_dir, exclude=None, is_print=True):
    """
    Decorator for caching function results.

    :param cache_dir: The directory where cached results will be stored.
    :param exclude: Parameters to exclude from the cache key, e.g., ['func_name', 'source_code', 'args'] (function name, source code, function arguments).
    :param is_print: Whether to print the cache process information.
    """

    if exclude is None:
        exclude = []

    def decorator(func):
        def wrapper(*args, **kwargs):
            source_code = inspect.getsource(func)

            params = inspect.signature(func).parameters

            args_dict = {name: kwargs.get(name) if name in kwargs else args[i] if i < len(args) else param.default for i, (name, param) in enumerate(params.items())}
            sorted(args_dict)
            args_dict.update(kwargs)

            modified_cache_dir = cache_dir.format(**args_dict)

            current_file_path = os.path.abspath(__file__)

            project_root = find_project_root(os.path.dirname(current_file_path))

            hash_key = []
            if 'func_name' not in exclude:
                hash_key.append(func.__name__)
            if 'source_code' not in exclude:
                tmp_source_code = source_code
                if 'func_name' not in exclude:
                    tmp_source_code = remove_unused_code(tmp_source_code)
                    tmp_source_code = tmp_source_code.replace(func.__name__, '')

                tmp_source_code = re.sub(r'\s', '', tmp_source_code)
                hash_key.append(tmp_source_code)
            if 'args' not in exclude:
                hash_key.append(str(args_dict))

            key = pickle.dumps(hash_key)
            file_name = hashlib.sha256(key).hexdigest() + '.pickle'
            file_path = os.path.join(project_root, modified_cache_dir, file_name)

            os.makedirs(os.path.join(project_root, modified_cache_dir), exist_ok=True)

            if os.path.exists(file_path):
                start = time.time()
                if is_print:
                    print(Fore.GREEN + f'{func.__name__} Loading from cache {file_path}', Style.RESET_ALL, end=' ')
                with open(file_path, 'rb') as f:
                    try:
                        result = pickle.load(f)
                    except:
                        result = func(*args, **kwargs)
                        with open(file_path, 'wb') as f:
                            pickle.dump(result, f)
                        if is_print:
                            print(Fore.YELLOW + f'{func.__name__} Saved to cache', file_path, Style.RESET_ALL)
                if is_print:
                    print(Fore.RED +f'{(time.time() - start):.1f}s ok', Style.RESET_ALL)
            else:
                result = func(*args, **kwargs)
                with open(file_path, 'wb') as f:
                    pickle.dump(result, f)
                if is_print:
                    print(Fore.YELLOW + f'{func.__name__} Saved to cache', file_path, Style.RESET_ALL)
            return result
        return wrapper
    return decorator
