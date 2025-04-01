from pydantic import BaseModel
from typing import List

class NodeData(BaseModel):
    name: str
    properties: dict

class LinkData(BaseModel):
    source: str
    target: str
    type: str
    properties: dict = {}
    label: str  # 新增label字段

class GraphResponse(BaseModel):
    nodes: List[NodeData]
    links: List[LinkData]