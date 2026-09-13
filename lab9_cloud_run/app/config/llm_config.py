from google.genai import types


CLASSIFIER_LLM_CONFIG = types.GenerateContentConfig(
    temperature=0.0,
    top_p=0.8,
    max_output_tokens=128,
    thinking_config=types.ThinkingConfig(
        thinking_budget=0,
        include_thoughts=False,
    ),
)


SPECIALIST_LLM_CONFIG = types.GenerateContentConfig(
    temperature=0.1,
    top_p=0.9,
    max_output_tokens=512,
    thinking_config=types.ThinkingConfig(
        thinking_budget=0,
        include_thoughts=False,
    ),
)