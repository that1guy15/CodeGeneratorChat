import os

GPT4Turbo_config = {
    "model": "gpt-4-turbo-preview",
    "api_key": os.environ.get("OPENAI_API_KEY"),
}

GPT4_config = {"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}

GPT35Turbo_config = {
    "model": "gpt-3.5-turbo",
    "api_key": os.environ.get("OPENAI_API_KEY"),
}
