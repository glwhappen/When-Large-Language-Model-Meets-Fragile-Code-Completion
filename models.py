from typing import List

from pydantic import BaseModel

class Complete(BaseModel):
    row_code: str = None
    prompt: str = None
    complete_code: str = None
    complete_tokens: int = None
    prompt_tokens: int = None


class Line(BaseModel):
    pos: int
    index: int
    line: str


class HugeCode(BaseModel):
    """
    - version_dir: Version directory
    - file_name: File name
    - huge_content_list: List of error code content
    - right_content_list: List of correct code content
    - huge_content_str: String of error code content
    - right_content_str: String of correct code content
    - similarity_huge_to_right: Similarity between error code and correct code
    - similarity_complete_to_huge: Similarity between completed code and error code
    - similarity_complete_to_right: Similarity between completed code and correct code

    - change_code: Equivalent transformed code
    - change_pre_code: Equivalent transformed code before completion
    - change_complete_code: Equivalent transformed code after completion

    - complete: Completed code
    """
    version_dir: str = None
    file_name: str  # File name
    huge_content_list: list[Line]  # List of error code content
    right_content_list: list[Line]  # List of correct code content
    huge_content_str: str  # String of error code content
    right_content_str: str   # String of correct code content

    similarity_huge_to_right: float = None  # Similarity between error code and correct code
    similarity_complete_to_huge: float = None  # Similarity between completed code and error code
    similarity_complete_to_right: float = None  # Similarity between completed code and correct code

    change_pre_code: str = None  # Equivalent transformed code before completion
    change_complete_code: str = None  # Equivalent transformed code after completion

    function_code_str: str = None
    function_code_pre_str: str = None

    huge_content_list_pre: list[Line] = None  # List of error code content before completion
    huge_content_list_complete: list[Line] = None  # List of error code content after completion

    right_content_list_pre: list[Line] = None  # List of correct code content before completion
    right_content_list_complete: list = None  # List of correct code content after completion

    complete: Complete = None  # Final completion result



def code_line2str(lines: list[Line]) -> str:
    return ''.join([line.line for line in lines])

def code_str2line(s: str) -> List[Line]:
    lines = s.split('\n')  # Split the string into lines
    return [Line(pos=0, index=0, line=line + '\n') for line in lines[:-1]]

class CompleteResult(BaseModel):
    sim_right: int = 0
    sim_wrong: int = 0
    right: int = 0
    wrong: int = 0
    error: int = 0
    total: int = 0

    def __str__(self):
        return f"Total {self.total} entries：\nNearly Correct: {self.sim_right}({(self.sim_right / self.total) * 100:.2f}%)\nNearly Wrong: {self.sim_wrong}({(self.sim_wrong / self.total) * 100:.2f}%)\nCompletely Correct: {self.right}({(self.right / self.total) * 100:.2f}%)\nCompletely Wrong: {self.wrong}({(self.wrong / self.total) * 100:.2f}%)\nNon-Compliant:{self.error}({(self.error / self.total) * 100:.2f}%)"

    def get_percentages(self):
        return [
            (self.sim_right / self.total) * 100,
            (self.sim_wrong / self.total) * 100,
            (self.right / self.total) * 100,
            (self.wrong / self.total) * 100,
            (self.error / self.total) * 100
        ]

    def to_dict(self):
        return {
            "补全接近正确": self.sim_right,
            "补全接近错误": self.sim_wrong,
            "补全完全正确": self.right,
            "补全完全错误": self.wrong,
            "补全不符合": self.error,
            "总量": self.total
        }

