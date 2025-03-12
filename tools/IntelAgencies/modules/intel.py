from dataclasses import dataclass, field, asdict, is_dataclass
import json

@dataclass
class Meta:
    country: str = None
    country_name: str = None
    refs: list = field(default_factory=list)
    synonyms: list = field(default_factory=list)
    
def custom_asdict(obj):
    if is_dataclass(obj):
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            if field_name == 'meta': 
                meta_value = custom_asdict(value)
                meta_value = {k: v for k, v in meta_value.items() if v is not None and not (k in ['refs', 'synonyms'] and (not v or all(e is None for e in v)))}
                value = meta_value
            elif isinstance(value, (list, tuple)) and all(is_dataclass(i) for i in value):
                value = [custom_asdict(i) for i in value]
            elif isinstance(value, list) and all(e is None for e in value):
                continue
            if value is None and field_name in ['country', 'country_name']:
                continue
            result[field_name] = value
        return result
    else:
        return obj

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
class Cluster:
    authors: str
    category: str
    description: str
    name: str
    source: str
    type: str
    uuid: str
    version: int
    values: list = field(default_factory=list)

    def add_value(self, value: IntelAgency):
        self.values.append(value)

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(json.dumps(custom_asdict(self), indent=4, ensure_ascii=False))