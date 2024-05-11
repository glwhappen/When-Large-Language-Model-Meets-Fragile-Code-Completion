import functools
import os
import time


def retry(max_retries=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Exception occurred while executing {func.__name__}: {str(e)}")
                    retries += 1
                    if retries >= max_retries:
                        print(f"Reached maximum retry attempts ({max_retries}), giving up on {func.__name__}")
                    else:
                        print(f"Retry {retries}/{max_retries}")
            return None  # 或者抛出异常或其他处理方式，取决于需要
        return wrapper
    return decorator


def find_project_root(current_dir = os.getcwd()):
    """
    向上搜索直到找到标识文件，确定项目的根目录
    """
    # 检查当前目录是否包含标识文件
    if os.path.isfile(os.path.join(current_dir, '.projectroot')):
        return current_dir
    # 获取上一级目录
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        # 已经到达了文件系统的根目录
        raise FileNotFoundError("无法找到项目根目录标识文件, 请在项目根目录下创建 .projectroot 文件.")
    # 递归继续向上搜索
    return find_project_root(parent_dir)


def timer(func):
    """装饰器，用于测量函数执行时间"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 执行函数
        end_time = time.time()  # 记录结束时间
        print(f"{func.__name__} ran in {end_time - start_time:.4f} seconds")  # 打印运行时间
        return result

    return wrapper