import openai
from cache_result import cache

from code_complete.token_tools import get_openai_token_len
from models import Complete
from tools.ConfigManager import ConfigManager

config_manager = ConfigManager()

@cache(cache_dir='./cache/completion/openai/{model}/{temperature}/{max_tokens}', exclude=['func_name', 'source_code'])
def row_complete(
    model="text-davinci-003",
    prompt='',
    temperature=0.7,
    max_tokens=200,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0):

    openai.api_key = config_manager.get_param('openai-gpt3', 'api_key', 'sk-xxx')
    openai.api_base = config_manager.get_param('openai-gpt3', 'api_base', 'https://api.openai.com/v1')

    res = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
        )
    if res['choices'][0]['text'] == '':
        raise Exception("openai return None")

    return res

@cache(cache_dir='./cache/completion/openai/{model}/{random}/{temperature}/{max_tokens}', exclude=['func_name', 'source_code'])
def row_complete_random(
    model="text-davinci-003",
    prompt='',
    temperature=0.7,
    max_tokens=200,
    top_p=1,
    frequency_penalty=0,
    random=1,
    presence_penalty=0):

    openai.api_key = config_manager.get_param('openai-gpt3', 'api_key', 'sk-xxx')
    openai.api_base = config_manager.get_param('openai-gpt3', 'api_base', 'https://api.openai.com/v1')

    res = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
        )
    if res['choices'][0]['text'] == '':
        raise Exception("openai return None", f"prompt:{prompt}", "error:", res)

    return res

def row_complete_no_cache(
    model="text-davinci-003",
    prompt='',
    temperature=0.7,
    max_tokens=200,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0):

    openai.api_key = config_manager.get_param('openai-gpt3', 'api_key', 'sk-xxx')
    openai.api_base = config_manager.get_param('openai-gpt3', 'api_base', 'https://api.openai.com/v1')

    res = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
        )
    print(res)
    if res['choices'][0]['text'] == '':
        raise Exception("openai return None")

    return res

import requests
import json
@cache(cache_dir='./cache/completion/openai/{model}/{temperature}/{max_tokens}', exclude=['func_name', 'source_code'])
def row_complete_gpt4(
    model="gpt4",
    prompt='',
    temperature=0.7,
    max_tokens=200,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0):

    url = config_manager.get_param('openai-gpt4', 'chat_api_base', 'https://oneapi.xty.app/v1/chat/completions')
    api_key = config_manager.get_param('openai-gpt4', 'api_key', 'sk-xxx')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    code = prompt

    _prompt = f"I need to complete the following code snippet. Please provide only the continuation of the code, without any additional comments or repeating the original code. The code is as follows:\n{code}"

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a code completion assistant."},
            {"role": "user", "content": _prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        completed_code = response.json()['choices'][0]['message']['content']
        if completed_code == '':
            raise Exception("openai return None")
        return completed_code
    else:
        print("Error:", response.status_code, response.text)
        raise Exception(response.text)



def complete(code, temperature = 0.7, max_tokens=200, prompt_max_tokens = 1000, model='gpt-3.5-turbo-instruct') -> Complete:
    code = reduce_token_length(code, prompt_max_tokens)


    if model == 'gpt-4':
        response = row_complete_gpt4(prompt=code, temperature=temperature, max_tokens=max_tokens, model=model)
        return Complete(
            row_code=code,
            complete_code=response,
            complete_tokens=0,
            prompt_tokens=0,
        )
    else:
        response = row_complete(prompt=code, temperature=temperature, max_tokens=max_tokens, model=model)

        return Complete(
            row_code=code,
            complete_code=response["choices"][0]["text"],
            complete_tokens=response["usage"]["completion_tokens"],
            prompt_tokens=response["usage"]["prompt_tokens"],
        )

def complete_random(code, temperature = 0.7, max_tokens=200, prompt_max_tokens = 1000, model='gpt-3.5-turbo-instruct', random=1) -> Complete:
    code = reduce_token_length(code, prompt_max_tokens)

    response = row_complete_random(prompt=code, temperature=temperature, max_tokens=max_tokens, model=model)

    return Complete(
        row_code=code,
        complete_code=response["choices"][0]["text"],
        complete_tokens=response["usage"]["completion_tokens"],
        prompt_tokens=response["usage"]["prompt_tokens"],
    )

# Reduce token length
def find_split_position(code, prompt_max_tokens):
    # Initialize left and right pointers within the range of the code string
    left, right = 0, len(code)

    # Binary search for the appropriate split position
    while left < right:
        mid = (left + right) // 2
        # Get the substring from the middle point to the end of the code
        mid_code = code[mid:]
        # Calculate the token length
        mid_token_len = get_openai_token_len(mid_code)

        if mid_token_len > prompt_max_tokens:
            # If the number of tokens from the middle point to the end is too many, move the left boundary to the right
            left = mid + 1
        else:
            # If the number of tokens is less than or equal to the maximum token count, move the right boundary to the left
            right = mid

    # Return the character position, representing the starting index of the code to be retained
    return right


def reduce_token_length(code, prompt_max_tokens=1000):
    # If the token length of the code is already below the limit, no reduction is needed
    if get_openai_token_len(code) <= prompt_max_tokens:
        return code

    # Find the starting index of the code to be retained
    split_position = find_split_position(code, prompt_max_tokens)

    # Slice the string based on the found position
    return code[split_position:]


if __name__ == '__main__':
    code = """    public static boolean equal(Polygon p1, Polygon p2) {
        if (p1 == null) {
            return (p2 == null);
        }
        if (p2 == null) {
            return false;
        }
        if (p1.npoints != p2.npoints) {
            return false;
        }
        if (!Arrays.equals(p1.xpoints, p2.xpoints)) {
            return false;
        }
        if (!Arrays.equals(p1.ypoints, p2.ypoints)) {
            return false;
        }
        return true;
    }

    /**
     * Tests two polygons for equality.  If both are <code>null</code> this
     * method returns <code>true</code>.
     *
     * @param p1  path 1 (<code>null</code> permitted).
     * @param p2  path 2 (<code>null</code> permitted).
     *
     * @return A boolean.2
     */
    public static boolean equal(GeneralPath p1, GeneralPath p2) {
        if (p1 == null) {
            return (p2 == null);
        }
        if (p2 == null) {
            return false;
        }
        if (p1.getWindingRule() != p2.getWindingRule()) {
            return false;
        }
        PathIterator iterator1 = p1.getPathIterator(null);
 """
    code = '       double denominator = d * q + c;\n            return createComplex((imaginary * q + real) / denominator,\n                (imaginary - real * q) / denominator);\n        }\n    }\n    \n    /**\n     * Test for the equality of two Complex objects.\n     * <p>\n     * If both the real and imaginary parts of two Complex numbers\n     * are exactly the same, and neither is <code>Double.NaN</code>, the two\n     * Complex objects are considered to be equal.</p>\n     * <p>\n     * All <code>NaN</code> values are considered to be equal - i.e, if either\n     * (or both) real and imaginary parts of the complex number are equal\n     * to <code>Double.NaN</code>, the complex number is equal to \n     * <code>Complex.NaN</code>.</p>\n     *\n     * @param other Object to test for equality to this\n     * @return true if two Complex objects are equal, false if\n     *         object is null, not an instance of Complex, or\n     *         not equal to this Complex instance\n     * \n     */\n    public boolean equals(Object other) {\n        boolean ret;\n        \n        if (this == other) { \n            ret = true;\n        } else if (other == null) {\n            ret = false;\n        } else  {\n            try {\n                Complex rhs = (Complex)other;\n                if (rhs.isNaN()) {\n                    ret = this.isNaN();\n                } else {1\n'
    code = '/*\n * Copyright (c) 2007 Mockito contributors\n * This program is made available under the terms of the MIT License.\n */\npackage org.mockito.internal.configuration.injection.filter;\n\nimport org.mockito.internal.util.MockUtil;\n\nimport java.lang.reflect.Field;\nimport java.util.ArrayList;\nimport java.util.Collection;\nimport java.util.List;\n\npublic class NameBasedCandidateFilter implements MockCandidateFilter {\n\tprivate final MockCandidateFilter next;\n\tprivate final MockUtil mockUtil = new MockUtil();\n\n\tpublic NameBasedCandidateFilter(MockCandidateFilter next) {\n\t\tthis.next = next;\n\t}\n\n\tpublic OngoingInjecter filterCandidate(Collection<Object> mocks,\n'
    response = complete_random(random=1, code=code, temperature=1.9, max_tokens=50, prompt_max_tokens=600, model="gpt-3.5-turbo-instruct")
    print(response)

