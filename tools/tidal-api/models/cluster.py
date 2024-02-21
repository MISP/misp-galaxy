import json

class Cluster():
    def __init__(self, authors: str, category: str, description: str, name: str, source: str, type: str, uuid: str, values: list, internal_type: str):
        self.authors = authors
        self.category = category
        self.description = description
        self.name = name
        self.source = source
        self.type = type
        self.uuid = uuid
        self.values = values
        self.internal_type = internal_type

    def add_value(self, value):
        self.values.append(value)
        
    def save_to_file(self, path):
        with open(path, "w") as file:
            file.write(json.dumps(self.__dict__, indent=4))

    def get_config(self):
        return self.__dict__
