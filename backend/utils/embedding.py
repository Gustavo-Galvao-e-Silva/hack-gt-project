from typing import Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")

def _get_similarity(node_list: list[dict[str, Any]], mode: str = "title") -> np.ndarray:
    if mode == "title":
        texts = [node["title"] for node in node_list]
        return cosine_similarity(model.encode(texts))

    elif mode == "description":
        texts = [node.get("description", "") for node in node_list]
        return cosine_similarity(model.encode(texts))

    elif mode == "hybrid":
        titles = model.encode([node["title"] for node in node_list])
        descs = model.encode([node.get("description", "") for node in node_list])

        # normalize similarities
        sim_titles = cosine_similarity(titles)
        sim_descs = cosine_similarity(descs)

        # weighted sum (you can tweak weights)
        return 0.6 * sim_titles + 0.4 * sim_descs

    else:
        raise ValueError("mode must be 'title', 'description', or 'hybrid'")


def find_connected_nodes(
        node_list: list[dict[str, Any]],
        min_similarity: float,
        max_similarity: float,
        mode: str = "title"
) -> list[dict[str, Any]]:
    similarity_matrix = _get_similarity(node_list, mode=mode)
    n = len(node_list)

    for node in node_list:
        node["connected_titles"] = []

    for i in range(n):
        for j in range(i + 1, n):
            similarity_score = similarity_matrix[i][j]
            if min_similarity <= similarity_score <= max_similarity:
                node_list[i]["connected_titles"].append({
                    "title": node_list[j]["title"],
                    "similarity": float(similarity_score)
                })
                node_list[j]["connected_titles"].append({
                    "title": node_list[i]["title"],
                    "similarity": float(similarity_score)
                })

    return node_list
