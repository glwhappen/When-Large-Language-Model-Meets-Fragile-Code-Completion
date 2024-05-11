from cache_result import cache
from code_complete_flow.huggingface_api import flow_huggingface_complete


@cache("cache/temp/compare_temperature/{model}")
def compare_temperature(model, max_workers = 1, max_tokens = 50, prompt_max_tokens = 600):
    count_result_list = []
    descriptions = []

    for i in range(1, 17, 1):
        lcs_wight = 0.5
        temperature = i / 10
        print(f"{model} run temperature {temperature}")
        _, count_result, max_token, prompt_max_token = flow_huggingface_complete(max_tokens=max_tokens,
                                                                                             prompt_max_tokens=prompt_max_tokens,
                                                                                lcs_weight=lcs_wight, led_weight=1-lcs_wight, model=model, random=1, newpayload={}, temperature=temperature, max_workers=max_workers)

        count_result_list.append(count_result.to_dict())
        descriptions.append(f"{model} complete lcs_weight={lcs_wight}, led_weight={1 - lcs_wight}, temperature={temperature}, max_tokens={max_tokens}, prompt_max_tokens={prompt_max_tokens}")


    return count_result_list, descriptions

def main():
    max_workers = 10

    compare_temperature(model="openai/gpt-3.5-turbo-instruct", max_workers=max_workers)
    # check(model="bigscience/bloom")
    compare_temperature(model="bigscience/bloom", max_workers=max_workers)
    # check(model="google/gemma-7b")
    compare_temperature(model="google/gemma-7b", max_workers=max_workers)
    # check(model="codellama/CodeLlama-13b-hf")
    compare_temperature(model="codellama/CodeLlama-13b-hf", max_workers=max_workers)
    # check(model="bigcode/starcoder2-15b")
    compare_temperature(model="bigcode/starcoder2-15b", max_workers=max_workers)
    # check(model="Salesforce/codegen-350M-multi")
    compare_temperature(model="Salesforce/codegen-350M-multi", max_workers=5)


if __name__ == '__main__':
    main()