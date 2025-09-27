from backend.prompts.extract_information import extract_system_prompt, extract_user_prompt

def extract_information_prompts(markdown: str) -> tuple[str, str]:
    system_prompt = extract_system_prompt
    user_prompt = extract_user_prompt.format(markdown)

    return system_prompt, user_prompt