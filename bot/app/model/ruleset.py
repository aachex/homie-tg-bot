from dataclasses import dataclass

@dataclass
class Ruleset:
    smoking: bool = False
    children: bool = False
    pets: bool = False