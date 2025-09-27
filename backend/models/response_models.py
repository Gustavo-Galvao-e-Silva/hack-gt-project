from pydantic import BaseModel, Field
from typing import Optional, List

class ConceptNode(BaseModel):
    title: Optional[str] = Field(
        default=None,
        description="Title of the node, should be a short word that identifies the concept this node refers to. For example, if this node talks about th concept of general relativity in the notes, this field should be 'General Relativity'.'"
    )
    connections: Optional[List[str]] = Field(
        default_factory=list,
        description="Titles of all other nodes connected to this node. The nodes should be conceptually related and always represented in the notes given. They should follow the consistent formating of correct capitalization. These connections should only be to concepts and terms in the notes provided, and **SHOULD NOT** be extrapolated from any other sources, only inferred from the notes given."
    )
    description: Optional[str] = Field(
        default=None,
        description="Short paragraph description on what is written about this topic on the notes, also relating to the other topics it is connected to. This description should only be about concepts and terms in the notes provided and very obvious aspects about the topic, and **SHOULD NOT** be extrapolated from any other sources, only inferred from the notes given."
    )

class ConceptNodeList(BaseModel):
    nodes: Optional[List[ConceptNode]] = Field(
        default_factory=list,
        description="List of all the concept nodes found in the notes. None should be extrapolated from any other sources, only inferred from the notes given."
    )