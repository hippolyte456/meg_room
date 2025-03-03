from pydantic import BaseModel
from typing import List

class ButtonConfig(BaseModel):
    label: str
    ttl: str
    status: str

class ResponseButtonsConfig(BaseModel):
    used_ports: List[str]
    buttons: List[ButtonConfig]

class MEGConfig(BaseModel):
    response_buttons: ResponseButtonsConfig
