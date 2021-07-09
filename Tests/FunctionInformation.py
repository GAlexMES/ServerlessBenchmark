from dataclasses import dataclass


@dataclass
class FunctionInformation:
    path:str
    url: str or None
    detail:str or None
