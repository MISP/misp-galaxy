import os
import json
import sys
import fnmatch
import uuid
import inspect

class ObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj

class Malpedia(object):

    def __init__(self, authors, description, name, source, type, folder_path, version=1):
        self.authors = authors
        self.description = description
        self.name = name
        self.source = source
        self.type = type
        self.uuid = str(uuid.uuid4())
        self.version = version
        self.values = self.get_files(folder_path)

    def get_files(self, folder_path):
        galaxies = []
        for root, dirnames, filenames in os.walk(folder_path):
            for filename in fnmatch.filter(filenames, '*.json'):
                with open(os.path.join(root, filename), 'r') as f:
                    json_dict = json.loads(
                        "".join([str(x) for x in f.readlines()]))
                    galaxies.append(
                        Galaxy(
                            description = json_dict.get("description", None),
                            value = json_dict.get("common_name", None),
                            synonyms = json_dict.get("alt_names", []),
                            refs = json_dict.get("urls", [])
                        ))
        return galaxies

class Galaxy(object):
    def __init__(self, description, value, synonyms=[], refs=[], type=[]):
        self.description = description
        self.value = value
        self.uuid = str(uuid.uuid4())
        self.meta = {}
        # duplicate item in array generate errors
        self.meta['refs'] = list(set(refs)) 
        self.meta['synonyms'] = list(set(synonyms))
        self.meta['type'] = type

a = Malpedia(authors=['Daniel Plohmann', 'Andrea Garavaglia', 'Davide Arcuri'], 
    description='Malware galaxy based on Malpedia archive.', 
    name='Malpedia', 
    source='Malpedia', 
    type='malpedia', 
    folder_path=os.environ['malpedia_path'], # this require cloned malpedia repository
    version=1) 

with open('../clusters/malpedia.json', 'w') as fp:
    json.dump(a, fp, cls=ObjectEncoder, indent=4)
