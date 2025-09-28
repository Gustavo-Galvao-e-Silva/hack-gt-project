from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO

from backend.utils.preprocessing import convert_file_to_md
from backend.utils.models import extract_completion
from backend.utils.find_connections import find_connected_nodes
from backend.prompts.prompt_building import extract_information_prompts


app = FastAPI()

@app.post("/graphs/upload_nodes")
async def upload_nodes(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File required")

        markdown = convert_file_to_md(BytesIO(content))
        system_prompt, user_prompt = extract_information_prompts(markdown)
        nodes = extract_completion(system_prompt, user_prompt)["nodes"]
        connected_nodes = find_connected_nodes(nodes, 0.45, 0.95, "hybrid") # TODO: look into tweaking the threshold

        return connected_nodes# TODO: Upload this to the DB ad just return a

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")


@app.get(f"/graphs/get_nodes")
async def get_nodes():
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")


@app.post("users/create_user")
async def create_user():
    pass