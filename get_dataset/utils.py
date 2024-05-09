import os
import pickle

from get_dataset.file_dir_work import get_all_file_name # Traverse directories to get all file names

def readIn(file_name, dir):
    """
    Read and deserialize a binary file from the specified directory.

    This function uses the pickle library to load and deserialize binary files.
    It is primarily used for reading pre-stored data structures or objects.

    :param file_name: The name of the file to read (string).
    :param dir: The directory path containing the file (string).
    :return: The deserialized object or data.
    """
    print('readIn', os.path.join(dir, file_name))
    with open(os.path.join(dir, file_name), 'rb') as file:
        a = pickle.load(file)
        return a


def readLine(file_name, line_num):
    """
    Read and return the content of the line with the specified line number from the file.

    This function opens a text file and returns the content of the specified line number.
    If the line number does not exist, it returns None.

    :param file_name: The name of the file to read (string).
    :param line_num: The line number to read (integer, counting from 1).
    :return: The content of the specified line (string), or None if the line number does not exist.
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if i == line_num - 1:
                return line
        return None

def readRangeLine(file_name, begin, end):
    """
    Read all lines within the specified range of line numbers from the file.

    This function returns the content of lines from the line number 'begin' to 'end' (including 'begin' but not 'end').
    The result is returned as a list, with each element representing the content of a line.

    :param file_name: The name of the file (string).
    :param begin: The starting line number (integer, counting from 0).
    :param end: The ending line number (integer, counting from 0).
    :return: A list containing the content of the specified lines (list of strings).
    """
    result = []
    with open(file_name, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            if begin <= i < end:
                result.append(line)

            if i == end:
                return result
    return result

def readFileLine(file_name, line_num):
    """
    Read and return the content of the line with the specified line number from the file.

    This function opens a text file and returns the content of the specified line number.
    If the line number does not exist, it returns None.

    :param file_name: The name of the file to read (string).
    :param line_num: The line number to read (integer, counting from 0).
    :return: The content of the specified line (string), or None if the line number does not exist.
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        for i, line in enumerate(file):
            print(i, line)
            if i == line_num:
                return line
        return None


def getHuge2Code(file_name, hugeToFile, hugeCode):
    """
    Retrieve relevant code from the hugeToFile and hugeCode files based on the specified file name.

    This function is used to find the content in the hugeCode file corresponding to a specific file name in the hugeToFile file.
    The result is returned as a list, with each element containing a line of code and its relevant information.

    :param file_name: The name of the source file to search for (string).
    :param hugeToFile: The file path containing the mapping of file names and line numbers (string).
    :param hugeCode: The file path containing the code content (string).
    :return: A list containing lines of code and their relevant information (list of dictionaries).
    """
    result = []
    with open(hugeToFile, 'r', encoding='utf-8') as file:
        pos = 1
        for i, line in enumerate(file):
            # todo: 这里可以优化，找到以后可以直接跳出代码
            if line.split('\t')[0] == file_name:
                result.append({
                    'line': '',
                    'index': i,
                    'pos': pos
                })
                pos += 1
            else:
                pos = 1

        file_content_list = readRangeLine(hugeCode, result[0]['index'], result[-1]['index'] + 1)
        # print(len(file_content_list), len(result))
        for i, line in enumerate(file_content_list):
            result[i]['line'] = line
    return result
from models import HugeCode
def getSrc(file_name:str, dir:str) -> HugeCode:
    """
    Get and construct a HugeCode object based on the given file name and directory.

    This function retrieves specific file content from the hugeCode.txt and hugeRightCode.txt files using the getHuge2Code function.
    The returned HugeCode object contains the content of the file and its correct version.

    :param file_name: The file name of the source file (string).
    :param dir: The directory containing the hugeCode.txt and hugeRightCode.txt files (string).
    :return: A HugeCode object containing the file content and other relevant information.
    """
    huge_content_list = getHuge2Code(file_name, f'{dir}/HugeToFile.txt', f'{dir}/hugeCode.txt')
    right_content_list = getHuge2Code(file_name, f'{dir}/HugeToRightFile.txt', f'{dir}/hugeRightCode.txt')
    # return HugeCode({
    #     'file': file_name,
    #     'content_list': huge_list,
    #     'huge_right_list': huge_right_list,
    #     'content': ''.join([item['line'] for item in huge_list])
    # })
    return HugeCode(file_name=file_name,
                    huge_content_list=huge_content_list,
                    right_content_list=right_content_list,
                    huge_content_str=''.join([item['line'] for item in huge_content_list]),
                    right_content_str=''.join([item['line'] for item in right_content_list]))


def get_completeOutput_version_dirs(dataset_path):
    """
    Get the paths of all subdirectories in the 'completeOutput' directory under the parent directory of the current working directory.

    This function is mainly used to retrieve the directory paths of all versions of code under the 'completeOutput' directory.
    The result is returned as a list, with each element representing a directory path.

    :return: A list containing the paths of 'completeOutput' subdirectories (list of strings).
    """
    print(dataset_path)
    # os.chdir(os.path.dirname(os.getcwd()) + '/completeOutput')
    # print(os.getcwd())
    return get_all_file_name(dataset_path)

