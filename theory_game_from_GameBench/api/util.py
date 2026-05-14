import importlib
import os
import json

def save_json(data, file_path):
    parent_dir = os.path.dirname(file_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_json(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"File {file_path} does not exist")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def import_class(class_path):
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
