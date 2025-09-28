from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from io import BytesIO

from backend.utils.preprocessing import convert_file_to_md
from backend.utils.models import extract_completion
from backend.utils.find_connections import find_connected_nodes
from backend.prompts.prompt_building import extract_information_prompts

from backend.db.db_ops import add_node, update_node, get_node, delete_node, get_all_nodes
from backend.db.connection import get_connection_from_env


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

        upload_nodes_db(connected_nodes, workspace_id)

        return  connected_nodes# TODO: Upload this to the DB and improve prompt to speed up graph generation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")


    
'''This function uploads the nodes to the database, checks if they're already there, and deletes nodes which are no longer in use.'''
# warning !! the code assumes that if you generate a new set of nodes, the id's still stay the same on the front end when parsing to the backend
def upload_nodes_db(nodes, workspace_id: int):
    """Uploads most recent nodes to the database."""
    try:
        conn = get_connection_from_env()  # retrieves a DB connection
        # Build a set of incoming node IDs for quick membership checks
        incoming_ids = set()
        for node in nodes:
            node_id = node.get("nodeID")
            title = node.get("title")
            description = node.get("description")
            connected_titles = node.get("connectedTitles")
            connected_ids = node.get("connectedIDs")
            workspace_id = node.get("workspaceID")

            if node_id is None:
                # skip malformed node entries
                continue

            incoming_ids.add(node_id)

            # if Node ID does not exist, create it, otherwise update it
            if get_node(conn, node_id, workspace_id) is None:
                add_node(conn, node_id, title, description, connected_titles, connected_ids, workspace_id)
            else:
                update_node(conn, node_id, title, description, connected_titles, connected_ids, workspace_id)

        # Clean up: fetch all existing node rows and delete those not present in the incoming set
        existing_rows = get_all_nodes(conn, workspace_id)
        for r in existing_rows:
            existing_id = r.get("nodeID")
            if existing_id is None:
                continue
            if existing_id not in incoming_ids:
                delete_node(conn, existing_id, workspace_id)
    finally:
        conn.close()  # Ensure the connection is closed after operations

'''This function retrieves all nodes from the database and returns them as JSON.'''
@app.get("/nodes/{workspace_id}")
def get_nodes(workspace_id: int):
    """Return all nodes from the database as JSON."""
    

    conn = get_connection_from_env()
    try:
        nodes = get_all_nodes(conn, workspace_id)
        return {"nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch nodes: {e}")
    finally:
        conn.close()
