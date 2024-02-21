import json

class Galaxy():
    def __init__(self, description, name, namespace, type, uuid, version):
        self.description = description
        self.name = name
        self.namespace = namespace
        self.type = type
        self.uuid = uuid
        self.version = version

    def save_to_file(self, path):
        with open(path, "w") as file:
            file.write(json.dumps(self.__dict__, indent=4))
