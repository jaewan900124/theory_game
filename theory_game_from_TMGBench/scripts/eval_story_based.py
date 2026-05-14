import argparse
from collections import Counter
from itertools import product
import json
import os
import random
import re
import sys
import textwrap
import time
from tqdm import tqdm

from models.gemma import Gemma
from models.gpt4 import GPT4
from models.llama3 import Llama3
from models.utils import tocls
from scripts.utils import color_print, parse_choice_combinations

def evaluate(llm, path, family, id, prompting, result_folder, show_response=False, num_tries=4, overwrite=False):
    output_path = f"{result_folder}/story-based/{family}_{id}_{llm}_{prompting}.json"
    if os.path.exists(output_path) and not overwrite:
        with open(output_path, "r") as file:
            if json.load(file).get("tries", 0) > 0:
                return

    task = open(f"{path}/{family}_{id}.txt", "r", encoding="utf-8", errors="replace")
    prompts = json.load(open(f"{path}/special_prompts.json"))

    desc = "\n".join(task.readlines())
    setting = prompts["context"]

    question = "[Question]\n" + prompts["question"] + "\n" + prompts[prompting] + "\n[/Question]"

    responses = []
    raw_responses = []
    parse_errors = []
    for tries in range(num_tries):
        llm.set_context(setting, role="system")
        response = llm.invoke(desc + "\n" + question)
        raw_responses.append(response)
        if show_response:
            print(f"\n===== {family}_{id} try {tries + 1} raw response =====")
            print(response)
            print("===== end raw response =====\n")
        try:
            choice_combinations = parse_choice_combinations(response)
            color_print(choice_combinations, "blue")
            responses.append(choice_combinations)
        except Exception as e:
            color_print(e, "red")
            color_print(response[:500], "yellow")
            parse_errors.append({"try": tries + 1, "error": str(e), "raw": response})
            continue
    print(responses)
    with open(output_path, "w") as file:
        json.dump({
            "attempted_tries": len(raw_responses),
            "tries": len(responses),
            "responses": responses,
            "raw_responses": raw_responses,
            "parse_errors": parse_errors,
        }, file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompting", "-p", type=str)
    parser.add_argument("--llm", "-s", type=str)
    parser.add_argument("--ver", "-v", type=str)
    parser.add_argument("--api_key", "-k", type=str)
    parser.add_argument("--base_url", "-l", type=str)
    parser.add_argument("--delay", "-d", type=str)
    parser.add_argument("--show_response", action="store_true")
    parser.add_argument("--tries", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    datasets_path = "dataset/story-based"
    result_folder = "results"
    os.makedirs(f"{result_folder}/story-based", exist_ok=True)

    llm = eval(r"""eval(tocls(args.llm))(
        api_key=args.api_key,
        base_url=args.base_url,
        version=args.ver
    )""")

    for id, layer, row, column in tqdm(product(range(0, 5),range(1, 5), range(1, 7), range(1, 7)), total=5 * 4 * 6 * 6):
        evaluate(llm, datasets_path, f"{layer}{row}{column}", id, args.prompting, result_folder, args.show_response, args.tries, args.overwrite)
        time.sleep(float(args.delay))

# 
