import validators

class Cluster:
    def __init__(self, uuid, galaxy, description=None, value=None, meta=None):
        self.uuid = uuid
        self.description = description
        self.value = value
        self.meta = meta

        self.galaxy = galaxy  # Reference to the Galaxy object this cluster belongs to
        self.outbound_relationships = set()
        self.inbound_relationships = set()
        self.relationships = set()

    def add_outbound_relationship(self, cluster):
        self.outbound_relationships.add(cluster)

    def add_inbound_relationship(self, cluster):
        self.inbound_relationships.add(cluster)

    def save_relationships(self, relationships):
        self.relationships = relationships

    def generate_entry(self):
        entry = ""
        entry += self._create_title_entry()
        entry += self._create_description_entry()
        entry += self._create_synonyms_entry()
        entry += self._create_uuid_entry()
        entry += self._create_refs_entry()
        entry += self._create_associated_metadata_entry()
        if self.relationships:
            entry += self._create_related_entry()
        return entry

    def _create_title_entry(self):
        entry = ""
        entry += f"## {self.value}\n"
        entry += f"\n"
        return entry

    def _create_description_entry(self):
        entry = ""
        if self.description:
            entry += f"{self.description}\n"
        return entry

    def _create_synonyms_entry(self):
        entry = ""
        if isinstance(self.meta, dict) and self.meta.get("synonyms"):
            entry += f"\n"
            entry += f'??? info "Synonyms"\n'
            entry += f"\n"
            entry += f'     "synonyms" in the meta part typically refer to alternate names or labels that are associated with a particular {self.value}.\n\n'
            entry += f"    | Known Synonyms      |\n"
            entry += f"    |---------------------|\n"
            synonyms_count = 0
            for synonym in sorted(self.meta["synonyms"]):
                synonyms_count += 1
                entry += f"     | `{synonym}`      |\n"
        return entry

    def _create_uuid_entry(self):
        entry = ""
        if self.uuid:
            entry += f"\n"
            entry += f'??? tip "Internal MISP references"\n'
            entry += f"\n"
            entry += f"    UUID `{self.uuid}` which can be used as unique global reference for `{self.value}` in MISP communities and other software using the MISP galaxy\n"
            entry += f"\n"
        return entry

    def _create_refs_entry(self):
        entry = ""
        if isinstance(self.meta, dict) and self.meta.get("refs"):
            entry += f"\n"
            entry += f'??? info "External references"\n'
            entry += f"\n"

            for ref in self.meta["refs"]:
                if validators.url(ref):
                    entry += f"     - [{ref}]({ref}) - :material-archive: :material-arrow-right: [webarchive](https://web.archive.org/web/*/{ref})\n"
                else:
                    entry += f"     - {ref}\n"

            entry += f"\n"
        return entry

    def _create_associated_metadata_entry(self):
        entry = ""
        if isinstance(self.meta, dict):
            excluded_meta = ["synonyms", "refs"]
            entry += f"\n"
            entry += f'??? info "Associated metadata"\n'
            entry += f"\n"
            entry += f"    |Metadata key {{ .no-filter }}      |Value|\n"
            entry += f"    |-----------------------------------|-----|\n"
            for meta in sorted(self.meta.keys()):
                if meta not in excluded_meta:
                    if meta == 'outcome':
                        self.meta[meta] = self.meta[meta].replace("\n", ".")
                    entry += f'    | {meta} | {self.meta[meta]} |\n'
        return entry

    def _create_related_entry(self):
        entry = ""
        entry += f"\n"
        entry += f'??? info "Related clusters"\n'
        entry += f"\n"
        entry += f"    To see the related clusters, click [here](./relations/{self.uuid}.md).\n"
        return entry
