from get_dataset.utils import readIn, readLine, getSrc

def find_file_name_by_fault_number(fault_number, dir):
    """
    Find the corresponding error file name and its internal error line number based on the provided fault number and directory.

    This function reads a file in a specific format (HugeToFile.txt), which maps line numbers of a large code file to individual source files and their line numbers.
    It returns the name of the source file containing the error and the line number within that source file.

    :param fault_number: The error line number in the large code file (integer).
    :param dir: The directory path containing HugeToFile.txt (string).
    :return: A tuple where the first element is the file name of the error source file (string), and the second element is the error line number within that source file (string).
    """
    faultHugeLine = readLine(f"{dir}/HugeToFile.txt", fault_number).split('\t')
    file_name = faultHugeLine[0]
    one_file_fault_number = faultHugeLine[1].split('\n')[0]
    return file_name, one_file_fault_number


def get_and_split_complete_code(dir = ''):
    """
    Retrieve code containing errors from the provided directory and split it into two parts.

    This function first reads a file in a specific format (faultHuge.in), which contains a series of error line numbers.
    For each error line number, the function finds the corresponding source file and the line number within the file.
    Then, it retrieves the content of the source file and splits it into two parts: the part before the error occurs and the part containing the error and after it.

    :param dir: The directory path containing relevant files (string).
    :return: A list of split source file objects, each containing the two parts of the file and other relevant information.
    """
    print("dir", dir)


    faultHuge = readIn("faultHuge.in", dir=dir) # {'/source/org/jfree/chart/renderer/category/AbstractCategoryItemRenderer.java': [116390]}

    result = []

    for key in faultHuge:

        if faultHuge[key] == []:
            continue

        file_name, one_file_fault_number = find_file_name_by_fault_number(faultHuge[key][0], dir=dir)
        all_fault_number = faultHuge[key][0]

        src_file = getSrc(file_name, dir=dir)
        huge_content_list = src_file.huge_content_list
        right_content_list = src_file.right_content_list
        pos = 0
        for item in huge_content_list:
            # print(item['index'], item['line'])
            if item.index == all_fault_number - 1:
                break
            pos += 1

        src_file.huge_content_list_pre = huge_content_list[:pos]
        src_file.huge_content_list_complete = huge_content_list[pos:]
        src_file.right_content_list_pre = right_content_list[:pos]
        src_file.right_content_list_complete = right_content_list[pos:]
        result.append(src_file)
    return result

