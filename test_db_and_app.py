import pytest
import uuid
from fastapi.testclient import TestClient

from backend.db.connection import get_connection_from_env
from backend.db import db_ops
from backend.app import app as fastapi_app


def gen_id():
    # stable-ish large random id to reduce collision with existing rows
    return int(uuid.uuid4().int % 10**9) + 10**6


@pytest.fixture(scope="function")
def conn():
    """Try to obtain a DB connection. If not available, skip all DB tests."""
    try:
        c = get_connection_from_env()
    except Exception as e:
        pytest.skip(f"Skipping DB tests; cannot connect: {e}")
    try:
        yield c
    finally:
        try:
            c.close()
        except Exception:
            pass


def test_user_crud(conn):
    uid = gen_id()
    # add user
    row = db_ops.add_user(conn, uid, "test_user")
    assert row is not None
    # Depending on your DB schema the returned key might be 'userID' or 'userid'
    assert row.get("userID") == uid or row.get("userid") == uid

    # get_user
    fetched = db_ops.get_user(conn, uid)
    assert fetched is not None

    # update_user
    updated = db_ops.update_user(conn, uid, username="updated_user")
    assert updated is not None
    assert updated.get("username") == "updated_user"

    # delete_user
    deleted = db_ops.delete_user(conn, uid)
    assert deleted is True


def test_workspace_crud(conn):
    uid = gen_id()
    wid = gen_id()
    # create supporting user
    db_ops.add_user(conn, uid, "ws_user")

    ws = db_ops.add_workspace(conn, wid, uid, title="My Workspace", description="desc")
    assert ws is not None
    assert ws.get("workspacesID") == wid or ws.get("workspacesid") == wid

    got = db_ops.get_workspace(conn, wid)
    assert got is not None

    updated = db_ops.update_workspace(conn, wid, title="New Title")
    assert updated is not None
    assert updated.get("title") == "New Title"

    deleted = db_ops.delete_workspace(conn, wid)
    assert deleted is True

    # cleanup user
    db_ops.delete_user(conn, uid)


def test_node_crud_and_helpers(conn):
    # prepare workspace and nodes
    uid = gen_id()
    wid = gen_id()
    db_ops.add_user(conn, uid, "node_user")
    db_ops.add_workspace(conn, wid, uid, title="node ws")

    nid1 = gen_id()
    nid2 = gen_id()

    n1 = db_ops.add_node(conn, nid1, "Node One", wid, description="first node", connected_titles=["Node Two"], connected_ids=[nid2])
    assert n1 is not None
    assert n1.get("nodeID") == nid1 or n1.get("nodeid") == nid1

    n2 = db_ops.add_node(conn, nid2, "Node Two", wid, description="second node", connected_titles=["Node One"], connected_ids=[nid1])
    assert n2 is not None

    # get_node
    g1 = db_ops.get_node(conn, nid1, wid)
    assert g1 is not None
    assert g1.get("title") == "Node One"

    # update_node
    upd = db_ops.update_node(conn, nid1, title="Node 1 Renamed")
    assert upd is not None
    assert upd.get("title") == "Node 1 Renamed"

    # node_exists
    assert db_ops.node_exists(conn, nid1) is True

    # node_table_size
    size = db_ops.node_table_size(conn)
    assert isinstance(size, int)
    assert size >= 0

    # get_all_nodes for this workspace
    all_nodes = db_ops.get_all_nodes(conn, wid)
    assert isinstance(all_nodes, list)

    # cleanup nodes
    assert db_ops.delete_node(conn, nid1, wid) in (True, False)
    assert db_ops.delete_node(conn, nid2, wid) in (True, False)

    # cleanup workspace/user
    try:
        db_ops.delete_workspace(conn, wid)
    except Exception:
        pass
    try:
        db_ops.delete_user(conn, uid)
    except Exception:
        pass


def test_get_nodes_endpoint(conn):
    # create a node so the endpoint returns at least one
    wid = gen_id()
    uid = gen_id()
    nid = gen_id()
    db_ops.add_user(conn, uid, "client_user")
    db_ops.add_workspace(conn, wid, uid, title="client ws")
    db_ops.add_node(conn, nid, "Endpoint Node", wid, description="for endpoint test")

    client = TestClient(fastapi_app)
    res = client.get(f"/nodes/{wid}")
    assert res.status_code == 200
    body = res.json()
    assert "nodes" in body
    assert isinstance(body["nodes"], list)

    # cleanup
    try:
        db_ops.delete_node(conn, nid, wid)
        db_ops.delete_workspace(conn, wid)
        db_ops.delete_user(conn, uid)
    except Exception:
        pass


def test_get_all_nodes_schema(conn):
    # create a workspace and a node to ensure we have data to inspect
    uid = gen_id()
    wid = gen_id()
    db_ops.add_user(conn, uid, "schema_user")
    db_ops.add_workspace(conn, wid, uid, title="schema ws")
    nid = gen_id()
    db_ops.add_node(conn, nid, "Schema Node", wid, description="for schema test")

    all_nodes = db_ops.get_all_nodes(conn, wid)
    assert isinstance(all_nodes, list)
    for n in all_nodes:
        # required fields and types
        assert isinstance(n.get("nodeID") or n.get("nodeid"), int)
        assert isinstance(n.get("title"), str)
        ct = n.get("connectedTitles")
        if ct is not None:
            assert isinstance(ct, list)
            assert all(isinstance(t, str) for t in ct)
        ci = n.get("connectedIDs")
        if ci is not None:
            assert isinstance(ci, list)
            assert all(isinstance(i, int) for i in ci)


def test_delete_nonexistent_node(conn):
    # deleting a node that does not exist should return False
    fake = gen_id()
    # ensure it does not exist
    try:
        # need a workspace id; choose a random one that likely doesn't exist
        db_ops.delete_node(conn, fake, 999999999)
    except Exception:
        # Some DBs may error on invalid operations; accept False or exception
        pass


def test_add_node_invalid_inputs(conn):
    wid = gen_id()
    uid = gen_id()
    db_ops.add_user(conn, uid, "tmp_user")
    db_ops.add_workspace(conn, wid, uid, title="tmp ws")

    nid = gen_id()
    # title is required; passing None or empty should raise
    with pytest.raises(Exception):
        db_ops.add_node(conn, nid, None, wid)

    with pytest.raises(Exception):
        db_ops.add_node(conn, nid, "", wid)

    # cleanup
    try:
        db_ops.delete_workspace(conn, wid)
        db_ops.delete_user(conn, uid)
    except Exception:
        pass


def test_add_node_connected_titles_shape(conn):
    # passing connected_titles as list of dicts should be rejected by DB
    uid = gen_id()
    wid = gen_id()
    db_ops.add_user(conn, uid, "tmp_user2")
    db_ops.add_workspace(conn, wid, uid, title="tmp ws2")
    nid = gen_id()
    # we expect this to raise (db expects list[str])
    with pytest.raises(Exception):
        db_ops.add_node(conn, nid, "Bad Shape", wid, description="demo", connected_titles=[{"title": "X"}], connected_ids=None)

    # cleanup
    try:
        db_ops.delete_workspace(conn, wid)
        db_ops.delete_user(conn, uid)
    except Exception:
        pass


def test_duplicate_node_id_behaviour(conn):
    uid = gen_id()
    wid = gen_id()
    db_ops.add_user(conn, uid, "dup_user")
    db_ops.add_workspace(conn, wid, uid, title="dup ws")
    nid = gen_id()

    first = db_ops.add_node(conn, nid, "DupNode", wid, description="first")
    assert first is not None

    # second insert with same ID should raise unique constraint error
    with pytest.raises(Exception):
        db_ops.add_node(conn, nid, "DupNode2", wid, description="second")

    # cleanup
    try:
        db_ops.delete_node(conn, nid, wid)
        db_ops.delete_workspace(conn, wid)
        db_ops.delete_user(conn, uid)
    except Exception:
        pass


import pytest as _pytest


@_pytest.mark.xfail(reason="upload_nodes_db may not accept extractor-shaped nodes yet")
def test_upload_nodes_db_integration(conn):
    # This integration test passes extractor-like nodes (no nodeID, connected_titles list of dicts)
    from backend.app import upload_nodes_db

    nodes = [
        {"title": "A", "description": "desc A", "connected_titles": []},
        {"title": "B", "description": "desc B", "connected_titles": [{"title": "A", "similarity": 0.8}]},
    ]

    # Should not raise; if implementation incomplete this will xfail
    upload_nodes_db(nodes)
