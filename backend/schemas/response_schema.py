from pydantic import BaseModel, Field
from typing import List, Optional

class ConceptNode(BaseModel):
    title: str = Field(
        ...,
        description="Short string that identifies this node's concept, e.g. 'Napoleon'. Must be exactly as written in the notes."
    )
    description: Optional[str] = Field(
        default=None,
        description="Short paragraph describing this concept, strictly based on the notes."
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Short list of keywords describing this concept from the notes and general topic knowledge",
    )

class ConceptNodeList(BaseModel):
    nodes: List[ConceptNode] = Field(
        default_factory=list,
        description="List of all concept nodes found in the notes. Do not include concepts not present in the notes."
    )
