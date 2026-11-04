import os
import json
import sys
import fnmatch
import uuid
import inspect

from galaxy_uuid import UuidAssigner, load_committed_cluster

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

# A malware family's uuid is its permanent identity -- other galaxies point at
# it through `related` edges. uuid4() minted a brand new one on every run, so
# regenerating this cluster replaced all ~2000 entries and orphaned every
# inbound reference. Derive from the family name instead, and reuse whatever
# is already committed.
UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'https://malpedia.caad.fkie.fraunhofer.de/')
CLUSTER_PATH = '../clusters/malpedia.json'
ASSIGNER = UuidAssigner(UUID_NAMESPACE, load_committed_cluster(CLUSTER_PATH))


class Malpedia(object):

    def __init__(self, authors, description, name, source, type, folder_path, version=1):
        self.authors = authors
        self.description = description
        self.name = name
        self.source = source
        self.type = type
        self.uuid = ASSIGNER.for_cluster('cluster')
        self.version = version
        self.values = self.get_files(folder_path)

    def get_files(self, folder_path):
        galaxies = []
        for root, dirnames, filenames in os.walk(folder_path):
            for filename in sorted(fnmatch.filter(filenames, '*.json')):
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
        self.uuid = ASSIGNER.for_value(value, synonyms=synonyms)
        self.meta = {}
        # duplicate item in array generate errors; set() ordering varies between
        # runs, so sort for a reproducible file
        self.meta['refs'] = sorted(set(refs))
        self.meta['synonyms'] = sorted(set(synonyms))
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
