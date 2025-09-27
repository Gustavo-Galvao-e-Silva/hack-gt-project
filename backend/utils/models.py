from openai import OpenAI
import json

from backend.config.config import OPEN_AI_KEY, OPEN_AI_MODEL
from backend.schemas.response_schema import ConceptNodeList


client = OpenAI(api_key=OPEN_AI_KEY)

def extract_completion(system_prompt, user_prompt: str) -> dict:
    response = client.chat.completions.create(
        model=OPEN_AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "concept_nodes",
                "schema": ConceptNodeList.model_json_schema()
            }
        }
    )

    content = response.choices[0].message.content
    return json.loads(content)
