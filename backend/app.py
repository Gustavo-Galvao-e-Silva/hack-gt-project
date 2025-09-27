from fastapi import FastAPI, File, UploadFile, HTTPException
from io import BytesIO

from backend.utils.preprocessing import convert_file_to_md
from backend.utils.models import extract_completion
from backend.utils.embedding import find_connected_nodes
from backend.prompts.prompt_building import extract_information_prompts


app = FastAPI()

@app.post("/documents/extract_nodes")
async def extract_nodes(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File required")

        markdown = convert_file_to_md(BytesIO(content))
        system_prompt, user_prompt = extract_information_prompts(markdown)
        nodes = extract_completion(system_prompt, user_prompt)["nodes"]
        connected_nodes = find_connected_nodes(nodes, 0.5, 0.9, "hybrid")

        # the upload to the DB
        upload_nodes_db(connected_nodes)

        return  connected_nodes# TODO: Upload this to the DB and improve prompt to speed up graph generation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")
    
# warning !! the code assumes that if you generate a new set of nodes, the id's still stay the same on the front end when parsing to the backend
def upload_nodes_db(nodes):
    """Uploads most recent nodes to the database."""
    from backend.db.db_ops import add_node, update_node, get_node, node_exists, delete_node, node_table_size
    from backend.db.connection import get_connection_from_env
    conn = get_connection_from_env()  # retrieves a DB connection
    try:
        for node in nodes:
            node_id = node.get("nodeID")
            title = node.get("title")
            description = node.get("description")
            connected_titles = node.get("connectedTitles")
            connected_ids = node.get("connectedIDs")
            workspace_id = node.get("workspaceID")
            # if Node ID does not exist, create it, otherwise update it
            if get_node(conn, node_id) is None:
                add_node(conn, node_id, title, description, connected_titles, connected_ids, workspace_id)
            else:
                update_node(conn, node_id, title, description, connected_titles, connected_ids, workspace_id)
        # Clean up any nodes that are no longer present via deletion, !! the bounds for this loop are prob wrong
        while node_id < node_table_size(conn):
            # if the node exists and is not in the new list, delete it
            if node_exists(conn, node_id) and node_id not in [n.get("nodeID") for n in nodes]:
                delete_node(conn, node_id)
            node_id += 1
    finally:
        conn.close()  # Ensure the connection is closed after operations