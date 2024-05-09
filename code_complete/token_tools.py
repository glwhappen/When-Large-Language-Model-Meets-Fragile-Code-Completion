import tiktoken

def get_openai_token_len(text, model="text-davinci-001"):
    """
    Get the token length of the prompt.
    masscode://snippets/0i8a-yjF
    https://github.com/openai/tiktoken
    :return:
    """

    enc = tiktoken.get_encoding("cl100k_base")
    assert enc.decode(enc.encode("hello world")) == "hello world"
    # To get the tokeniser corresponding to a specific model in the OpenAI API:
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    # print(tokens)
    # print(enc.decode(tokens))
    return len(tokens)

if __name__ == '__main__':
    code = """
    import openai
    print("hello world")
    """
    print("token length: ", get_openai_token_len(code))