import yaml
import json
import os

DEFAULT_CONFIG = {
    "LANGUAGE": "en",
    "INTERNET_ACCESS": False,
    "API_BASE_URL": "https://api.openai.com/v1",
    "MODEL_ID": "gpt-4o-mini",
}


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


config = DEFAULT_CONFIG.copy()
if os.path.exists("config.yml"):
    with open("config.yml", "r", encoding="utf-8") as config_file:
        config.update(yaml.safe_load(config_file) or {})

config["LANGUAGE"] = os.getenv("LANGUAGE", str(config["LANGUAGE"]))
config["INTERNET_ACCESS"] = _env_bool("INTERNET_ACCESS", bool(config["INTERNET_ACCESS"]))
config["API_BASE_URL"] = os.getenv("API_BASE_URL", str(config["API_BASE_URL"]))
config["MODEL_ID"] = os.getenv("MODEL_ID", str(config["MODEL_ID"]))

## Language settings ##
valid_language_codes = []
lang_directory = "lang"

current_language_code = config['LANGUAGE']

for filename in os.listdir(lang_directory):
    if filename.startswith("lang.") and filename.endswith(".json") and os.path.isfile(
            os.path.join(lang_directory, filename)):
        language_code = filename.split(".")[1]
        valid_language_codes.append(language_code)

def load_current_language() -> dict:
    lang_file_path = os.path.join(
        lang_directory, f"lang.{current_language_code}.json")
    with open(lang_file_path, encoding="utf-8") as lang_file:
        current_language = json.load(lang_file)
    return current_language

# Instructions loader
def load_instructions() -> dict:
    instructions = {}
    for file_name in os.listdir("instructions"):
        if file_name.endswith('.txt'):
            file_path = os.path.join("instructions", file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            # Use the file name without extension as the variable name
                variable_name = file_name.split('.')[0]
                instructions[variable_name] = file_content
    return instructions

def load_active_channels() -> dict:
    if os.path.exists("channels.json"):
        with open("channels.json", "r", encoding='utf-8') as f:
            active_channels = json.load(f)
    return active_channels
