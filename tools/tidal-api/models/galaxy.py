import json
from dataclasses import dataclass, asdict


@dataclass
class Galaxy:
    description: str
    icon: str
    name: str
    namespace: str
    type: str
    uuid: str
    version: str

    def save_to_file(self, path: str):
        with open(path, "w") as file:
            file.write(json.dumps(asdict(self), indent=2))
            file.write('\n')
