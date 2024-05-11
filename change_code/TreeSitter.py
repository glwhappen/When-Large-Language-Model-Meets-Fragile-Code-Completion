"""
封装tree-sitter
1. change_args can replace the parameters of a Java code function, and then return the replaced code.
    tree_sitter = TreeSitter(code)
    print(tree_sitter.change_args())

2023-04-26 11:43:00
"""
import os

from tree_sitter import Language, Parser

class TreeSitter():
    def __init__(self, code, language = 'java'):
        cur_path = os.path.dirname(__file__)
        JAVA_LANGUAGE = Language(f'{cur_path}/build/my-languages.so', language)

        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

        self.language = language
        self.code = code
        self.tree = self.parse()

        self.tree_list = []
        self.get_tree_list(self.tree)
    def get_tree(self):
        return self.parser.parse(bytes(self.code, 'utf-8'))
    def parse(self):
        tree = self.parser.parse(bytes(self.code, 'utf-8'))
        # print(tree.root_node.type)
        return tree.root_node

    def find_function(self, line_node):
        return self._find_function(self.get_tree().root_node, line_node)

    def _find_function(self, node, line_no):
        # print(node.type, node.start_point, node.end_point)
        if node.type == 'method_declaration' and node.start_point[0] <= line_no <= node.end_point[0]:

            start = node.start_byte
            end = node.end_byte
            return self.replace_strings_in_code(self.code[start:end]), node.start_point[0], node.end_point[0]
        # print(node.children)
        for child in node.children:
            # print(child.type, child.start_point, child.end_point)
            result, start_line, end_line = self._find_function(child, line_no)
            if result:
                return result, start_line, end_line
        return None, None, None

    def replace_strings_in_function(self, function_code):
        tree = self.parser.parse(bytes(function_code, 'utf-8'))

        def replace_strings(node):
            nonlocal function_code

            if node.type == 'string_literal':
                start = node.start_byte
                end = node.end_byte

                function_code = function_code[:start] + '" String_Node_Str "' + function_code[end:]
            for child in node.children:
                replace_strings(child)

        replace_strings(tree.root_node)
        return function_code

    def replace_strings_in_code(self, code):
        tree = self.parser.parse(bytes(code, 'utf-8'))
        # Accumulate replacements in a list to avoid changing string lengths during iteration
        replacements = []

        def collect_replacements(node):
            if node.type == 'string_literal':
                start = node.start_byte
                end = node.end_byte
                # Collect the replacement information
                replacements.append((start, end, '"String_Node_Str"'))
            for child in node.children:
                collect_replacements(child)

        collect_replacements(tree.root_node)
        # print(replacements)

        # Apply replacements from last to first to avoid offset issues
        for start, end, new_text in reversed(replacements):
            code = code[:start] + new_text + code[end:]

        return code


    def get_tree_list(self, node, depth=0):

        self.tree_list.append({
            'type': node.type,
            'start_point': node.start_point,
            'end_point': node.end_point,
            'text': node.text.decode('utf-8'),
            'depth': depth,
            'id': node.id,
            'is_named': node.is_named,
            'child_count': node.child_count,
            'parent_type': node.parent.type if node.parent else None,
        })

        for child in node.children:
            self.get_tree_list(child, depth=depth + 1)

    def get_change_args_list(self, type_params = False):

        tree_list = self.tree_list

        method_declaration = None
        parameter_list = {}

        change_arg_list = []  # [{index: ((0,0), (0,0)), old_name: '', new_name: ''}]

        for tree_item in tree_list:
            # print(tree_item)
            if tree_item['type'] == 'method_declaration':
                method_declaration = tree_item
            if tree_item['type'] == 'identifier' and tree_item['parent_type'] == 'method_declaration':
                method_declaration['name'] = tree_item['text']
            if method_declaration:
                if tree_item['type'] == 'identifier' and tree_item['parent_type'] == 'formal_parameter':

                    if method_declaration['id'] not in parameter_list:
                        parameter_list[method_declaration['id']] = []
                    # print(tree_item['text'], len(parameter_list[method_declaration['id']]))
                    parameter_list[method_declaration['id']].append(tree_item)

                if tree_item['type'] == 'identifier' and tree_item['parent_type'] not in ['method_declaration', 'field_access', 'method_invocation', 'variable_declarator']:
                    text = tree_item['text']
                    if method_declaration['id'] not in parameter_list:
                        continue
                    for parameter in parameter_list[method_declaration['id']]:
                        if text == parameter['text']:

                            if type_params:
                                change_arg_list.append({
                                    'index': (tree_item['start_point'], tree_item['end_point']),
                                    'old_name': tree_item['text'],
                                    'new_name': "param_" + parameter['text']
                                })
                            else:
                                change_arg_list.append({
                                    'index': (tree_item['start_point'], tree_item['end_point']),
                                    'old_name': tree_item['text'],
                                    'new_name': method_declaration['name'] + "_" + parameter['text']
                                })
        return change_arg_list

    def get_print_local_variable_list(self):
        """
        Get the list of printing local variables.
        :return: [{lineNumber: 1, text: ''}] lineNumber: line number, text: printed content. Return the position to be inserted.
        """
        local_variable_declaration = None

        tree_list = self.tree_list

        print_local_variable_list = [] # [{lineNumber: 1, text: ''}]

        for tree_item in tree_list:
            # print(tree_item)
            if tree_item['type'] == 'local_variable_declaration':
                local_variable_declaration = tree_item
            if local_variable_declaration and tree_item['type'] == 'identifier':
                print(f"System.out.println({tree_item['text']}) 在第{local_variable_declaration['end_point'][0] + 1}行插入")
                print(tree_item)
                print_local_variable_list.append({
                    'lineNumber': local_variable_declaration['end_point'][0] + 1,
                    'text': f"System.out.println({tree_item['text']});"
                })
                local_variable_declaration = None
        return print_local_variable_list

    def insert_print_local_variable(self):
        """
        Insert print statements for local variables.
        Print the value of each local variable.
        :return:
        """
        print_local_variable_list = self.get_print_local_variable_list()
        code = self.code
        if type(code) != list:
            code = code.split('\n')
        for print_local_variable in print_local_variable_list[::-1]:
            if print_local_variable['lineNumber'] >= len(code) - 3: # 最后的一行不进行插入，防止影响代码补全
                continue
            code.insert(print_local_variable['lineNumber'], print_local_variable['text'])
        return '\n'.join(code)

    def get_last_line_type(self):
        tree_list = self.tree_list

        start_point = tree_list[-1]['start_point'][0]
        # print("start_point", start_point)
        for tree in tree_list:
            if tree['start_point'][0] == start_point:
                # input("捕获到一条")
                # 只包含需要的
                if tree['type'] == 'enhanced_for_statement':
                    tree['type'] = 'for'
                if tree['type'] == 'if':
                    tree['type'] = 'if_statement'
                if tree['type'] == 'while':
                    tree['type'] = 'while_statement'
                # if tree['type'] in ['return_statement', 'local_variable_declaration', 'expression_statement',
                #                     'if_statement', 'import_declaration', 'throw_statement', 'field_declaration',
                #                     'while_statement', 'class_declaration', 'method_invocation', 'method_declaration', 'for']:
                if tree['type'] in ['return_statement', 'local_variable_declaration', 'expression_statement',
                                        'if_statement', 'field_declaration',
                                        'while_statement', 'method_invocation',
                                        'method_declaration', 'throw_statement', 'identifier', 'for']:

                    return tree
                else:
                    # with open('other.txt', 'a') as file:
                    #     file.writelines(tree['type'])
                    return {
                        "type": 'other'
                    }
                # else:
                #     return tree
        return None

    def get_last_line_type_by_pos(self, pos):
        tree_list = self.tree_list

        start_point = pos
        for tree in tree_list:
            if tree['start_point'][0] == start_point:
                return tree
        return None
    def change_args(self): # args = list [{index: ((0,0), (0,0)), old_name: '', new_name: ''}]
        """
        Change parameter names.
        :return:
        """
        code = self.code
        if type(code) != list:
            code = code.split('\n')
        change_arg_list = self.get_change_args_list()
        print(change_arg_list)
        change_arg_list = change_arg_list[::-1]
        for change_arg in change_arg_list:
            row = change_arg['index'][0][0]
            start_point = change_arg['index'][0]
            end_point = change_arg['index'][1]
            old_name = change_arg['old_name']
            new_name = change_arg['new_name']
            # code[row][start_point[1]:end_point[1]] = new_name
            line_row = list(code[row])
            line_row[start_point[1]:end_point[1]] = new_name
            code[row] = ''.join(line_row)
            # print(code[row][start_point[1]:end_point[1]], '替换', new_name)
        return '\n'.join(code)



if __name__ == '__main__':
    code = """class HelloChina{
        static void helloFun(String str, int a, int b){
            String name = str;
            int c = a + b;
            System.out.println("Hello World!" + str + c);
            return str;
        }
    	public static void main(String[] args){
    	    helloFun("China");
    		System.out.println("Hello World!");
    	}
    	static void helloFun(String str, int a, int b){
            String name = str; return a + b;

    """

#     code = """
#
# int g = (int) ((value - this.lowerBound) / (this.upperBound
#         v = Math.min(v, this.upperBound);
#         int g = (int) ((value - this.lowerBound) / (this.upperBound
#     """

    tree_sitter = TreeSitter(code)

    # print(tree_sitter.tree_list)
    for tree in tree_sitter.tree_list:
        print(tree)
