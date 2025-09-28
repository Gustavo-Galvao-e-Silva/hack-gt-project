from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from io import BytesIO

from backend.utils.preprocessing import convert_file_to_md
from backend.utils.models import extract_completion
from backend.utils.find_connections import find_connected_nodes
from backend.prompts.prompt_building import extract_information_prompts

from backend.db.db_ops import add_node, add_workspace, get_node_by_title, get_user_workspaces, get_workspace_highest_id, update_node, get_node, delete_node, get_all_nodes
from backend.db.connection import get_connection_from_env
from fastapi.responses import RedirectResponse
import hashlib
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def root():
    # Redirect to the interactive docs
    return RedirectResponse(url="/docs")

@app.get("/workspaces/{user_id}")
def get_workspaces(user_id: int):
    try:
        conn = get_connection_from_env()
        workspaces = get_user_workspaces(conn, user_id)
        return workspaces
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")
    finally:
        conn.close()
    
@app.post("/workspaces/create")
def create_workspace(user_id: int = Form(...), title: str = Form(...), description: str = Form(None)):
    try:
        conn = get_connection_from_env()
        workspace_id = get_workspace_highest_id(conn) + 1
        add_workspace(conn, workspace_id, user_id, title, description)
        return {"workspace_id": workspace_id, "user_id": user_id, "title": title, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {e}")
    finally:
        conn.close()

@app.post("/graphs/upload_nodes")
async def upload_nodes(file: UploadFile = File(...), workspace_id: int = Form(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File required")

        markdown = convert_file_to_md(BytesIO(content))
        system_prompt, user_prompt = extract_information_prompts(markdown)
        nodes = extract_completion(system_prompt, user_prompt)["nodes"]
        connected_nodes = find_connected_nodes(nodes, 0.45, 0.95, "hybrid") # TODO: look into tweaking the threshold
        upload_nodes_db(connected_nodes, workspace_id)

        return connected_nodes# TODO: Upload this to the DB and improve prompt to speed up graph generation

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong {e}")

# load initially
# @app.get("/graphs/load_nodes")
# async def load_nodes(workspace_id: int):
#     try:
#         conn = get_connection_from_env()
#         nodes = get_all_nodes(conn, workspace_id)
#         return nodes
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Something went wrong {e}")

'''This function uploads the nodes to the database, checks if they're already there, and deletes nodes which are no longer in use.'''
# warning !! the code assumes that if you generate a new set of nodes, the id's still stay the same on the front end when parsing to the backend
def upload_nodes_db(nodes, workspace_id: int):
    """Uploads most recent nodes to the database."""
    try:
        conn = get_connection_from_env()  # retrieves a DB connection
        print(nodes)
        print(type(nodes[0]))

        incoming_ids = set()
        title_id_dict = {}

        for node in nodes:
            node["node_id"] = generate_workspace_hash(workspace_id, node.get("title", ""))
            incoming_ids.add(node["node_id"])
            title_id_dict[node["title"]] = node["node_id"]

        # Build a set of incoming node IDs for quick membership checks
        
        for node in nodes:
            node_id = node.get("node_id")
            title = node.get("title")
            description = node.get("description")
            connected_titles = node.get("connectedTitles", []) # hypothetically should be fine
            connected_ids = [title_id_dict.get(t, None) for t in connected_titles]  # substitute titles with IDs
            keywords = node.get("keywords", [])  

            print(connected_ids)

            if node_id is None:
                # skip malformed node entries
                continue

            # if Node ID does not exist, create it, otherwise update it
            if get_node(conn, node_id, workspace_id) is None:
                add_node(conn, node_id, title, workspace_id, description, connected_titles, connected_ids, keywords)
            else:
                #update_node(conn, node_id, workspace_id, title, description, connected_titles, connected_ids, keywords)

                # join the two using UNION!

                #get the sql row that matches the node title
                sql_row = get_node_by_title(conn, title, workspace_id)
                node1 = set(sql_row.get("connectedIDs", []))
                node2 = set(connected_ids) if connected_ids is not None else set()
                union_connected_ids = list(node1.union(node2))
                update_node(conn, node_id, workspace_id, title, description, connected_titles, union_connected_ids, keywords)

        # Clean up: fetch all existing node rows and delete those not present in the incoming set
        # existing_rows = get_all_nodes(conn, workspace_id)
        # for r in existing_rows:
        #     existing_id = r.get("nodeID")
        #     if existing_id is None:
        #         continue
        #     if existing_id not in incoming_ids:
        #         delete_node(conn, existing_id, workspace_id)

        # add connected_titles and connected_ids to the nodes in the DB
        # for every node, look at its connected titles, and get their corresponding IDs from title_id_dict
        for node in nodes:
            print("hello")
            node_id = node.get("node_id")
            if node_id is None:
                continue
            print("ywasp")
            connectedTitles = []
            # for every connected title, get its corresponding ID from title_id_dict
            print(node.get("connected_titles", []))
            for cT in node.get("connected_titles", []):
                print(cT.get("title", ""))
                connectedTitles.append(cT.get("title", ""))
            connectedIds = [title_id_dict.get(t, None) for t in connectedTitles]  # substitute titles with IDs
            
            # Update the node with its connected titles and IDs
            update_node(conn, node_id, workspace_id, node.get("title"), node.get("description"), connectedTitles, connectedIds, node.get("keywords", []))
    except Exception as e:
        print(f"Error uploading nodes to DB: {e}")
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


def generate_workspace_hash(workspace_id, title):
    """
    Generate a numeric hash by combining workspace_id and title.
    
    Args:
        workspace_id (str): The workspace identifier
        title (str): The title string
    
    Returns:
        int: A numeric hash value
    """
    # Combine workspace_id and title with a delimiter
    combined_string = f"{workspace_id}:{title}"
    
    # Create SHA-256 hash of the combined string
    hash_object = hashlib.sha256(combined_string.encode('utf-8'))
    
    # Get the hexadecimal representation
    hex_hash = hash_object.hexdigest()
    
    # Convert to integer (you can also use a subset of the hex string for shorter numbers)
    numeric_hash = int(hex_hash, 16)

    number_str = str(numeric_hash)
    if len(number_str) >= 8:
        return int(number_str[:8])
    else:
        return numeric_hash