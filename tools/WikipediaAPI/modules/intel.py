from dataclasses import dataclass, field, asdict
import json

@dataclass
class Meta:
    country: str = ""

@dataclass
class IntelAgency:
    description: str = ""
    meta: Meta = field(default_factory=Meta)
    related: list = field(default_factory=list)
    uuid: str = None
    value: str = None

    def __post_init__(self):
            if not self.value:
                raise ValueError("IntelAgency 'value' cannot be empty.")
            if not self.uuid:
                 raise ValueError("IntelAgency 'uuid' cannot be empty.")
    
@dataclass
class Galaxy:
    description: str
    icon: str 
    name: str
    namespace: str
    type: str 
    uuid: str 
    version: int 

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(json.dumps(asdict(self), indent=4))

@dataclass
class Cluster():
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
        version: int,
    ):
        self.authors = authors
        self.category = category
        self.description = description
        self.name = name
        self.source = source
        self.type = type
        self.uuid = uuid
        self.version = version
        self.values = []

    def add_value(self, value: IntelAgency):
        self.values.append(value)

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(json.dumps(asdict(self), indent=4))