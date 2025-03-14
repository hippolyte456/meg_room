from pydantic import BaseModel
from typing import List


class ButtonConfig(BaseModel):
    label: str
    ttl: str
    status: str


class ResponseButtonsConfig(BaseModel):
    used_ports: List[str]
    buttons: List[ButtonConfig]


class EyelinkConfig(BaseModel):
    ip: str
    port: int
    used_ports: List[str]
    

class StimPCConfig(BaseModel):
    ip: str
    port: int
    used_ports: List[str]


class RoomConfig(BaseModel):
    response_buttons: ResponseButtonsConfig