from dataclasses import dataclass, field, asdict
import json


@dataclass
class Meta:
    pass


@dataclass
class GroupsMeta(Meta):
    source: str = None
    group_attack_id: str = None
    country: str = None
    observed_countries: list = None
    observed_motivations: list = None
    target_categories: list = None
    tags: list = None
    owner: str = None


@dataclass
class SoftwareMeta(Meta):
    source: str = None
    type: str = None
    software_attack_id: str = None
    platforms: list = None
    tags: list = None
    owner: str = None


@dataclass
class TechniqueMeta(Meta):
    source: str = None
    platforms: list = None
    tags: list = None
    owner: str = None


@dataclass
class SubTechniqueMeta(Meta):
    source: str = None
    technique_attack_id: str = None


@dataclass
class TacticMeta(Meta):
    source: str = None
    tactic_attack_id: str = None
    ordinal_position: int = None
    tags: list = None
    owner: str = None


@dataclass
class ReferencesMeta(Meta):
    source: str = None
    refs: list = None
    title: str = None
    author: str = None
    date_accessed: str = None
    date_published: str = None
    owner: str = None


@dataclass
class CampaignsMeta(Meta):
    source: str = None
    campaign_attack_id: str = None
    first_seen: str = None
    last_seen: str = None
    tags: list = None
    owner: str = None


@dataclass
class ClusterValue:
    description: str = ""
    meta: Meta = field(default_factory=Meta)
    related: list = field(default_factory=list)
    uuid: str = ""
    value: str = ""

    def return_value(self):
        value_dict = asdict(self)
        value_dict["meta"] = {
            k: v for k, v in asdict(self.meta).items() if v is not None
        }
        return value_dict


class Cluster:
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        self.authors = authors
        self.category = category
        self.description = description
        self.name = name
        self.source = source
        self.type = type
        self.uuid = uuid
        self.values = []

    def add_values(self):
        print("This method should be implemented in the child class")

    def save_to_file(self, path):
        with open(path, "w") as file:
            file.write(json.dumps(self.__dict__(), indent=4))

    def __str__(self) -> str:
        return f"Cluster: {self.name} - {self.type} - {self.uuid}"

    def __dict__(self) -> dict:
        return {
            "authors": self.authors,
            "category": self.category,
            "description": self.description,
            "name": self.name,
            "source": self.source,
            "type": self.type,
            "uuid": self.uuid,
            "values": self.values,
        }


class GroupCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = GroupsMeta(
                source=entry.get("source"),
                group_attack_id=entry.get("group_attack_id"),
                country=(
                    entry.get("country")[0].get("country_code")
                    if entry.get("country")
                    else None
                ),
                observed_countries=[
                    x.get("country_code") for x in entry.get("observed_country")
                ],
                observed_motivations=[
                    x.get("name") for x in entry.get("observed_motivation")
                ],
                target_categories=[x.get("name") for x in entry.get("observed_sector")],
                tags=[x.get("tag") for x in entry.get("tags")],
                owner=entry.get("owner_name"),
            )
            related = []
            for relation in entry.get("associated_groups"):
                related.append(
                    {
                        "dest-uuid": relation.get("id"),
                        "type": "related-to",
                    }
                )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())


class SoftwareCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = SoftwareMeta(
                source=entry.get("source"),
                type=entry.get("type"),
                software_attack_id=entry.get("software_attack_id"),
                platforms=[x.get("name") for x in entry.get("platforms")],
                tags=[x.get("tag") for x in entry.get("tags")],
                owner=entry.get("owner_name"),
            )
            related = []
            for relation in entry.get("groups"):
                related.append(
                    {
                        "dest-uuid": relation.get("group_id"),
                        "type": "used-by",
                    }
                )
            for relation in entry.get("associated_software"):
                related.append(
                    {
                        "dest-uuid": relation.get("id"),
                        "type": "related-to",
                    }
                )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())


class TechniqueCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = TechniqueMeta(
                source=entry.get("source"),
                platforms=[x.get("name") for x in entry.get("platforms")],
                tags=[x.get("tag") for x in entry.get("tags")],
                owner=entry.get("owner_name"),
            )
            related = []
            for relation in entry.get("tactic"):
                related.append(
                    {
                        "dest-uuid": relation.get("tactic_id"),
                        "type": "uses",
                    }
                )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())

            for sub_technique in entry.get("sub_technique"):
                meta = SubTechniqueMeta(
                    source=sub_technique.get("source"),
                    technique_attack_id=sub_technique.get("technique_attack_id"),
                )
                related = []
                for relation in sub_technique.get("tactic"):
                    related.append(
                        {
                            "dest-uuid": relation.get("tactic_id"),
                            "type": "uses",
                        }
                    )
                value = ClusterValue(
                    description=sub_technique.get("description"),
                    meta=meta,
                    related=related,
                    uuid=sub_technique.get("id"),
                    value=sub_technique.get("name"),
                )
                self.values.append(value.return_value())


class TacticCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = TacticMeta(
                source=entry.get("source"),
                tactic_attack_id=entry.get("tactic_attack_id"),
                ordinal_position=entry.get("ordinal_position"),
                tags=[x.get("tag") for x in entry.get("tags")],
                owner=entry.get("owner_name"),
            )
            related = []
            for relation in entry.get("techniques"):
                related.append(
                    {
                        "dest-uuid": relation.get("technique_id"),
                        "type": "uses",
                    }
                )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())


class ReferencesCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = ReferencesMeta(
                source=entry.get("source"),
                refs=[entry.get("url")],
                title=entry.get("title"),
                author=entry.get("author"),
                date_accessed=entry.get("date_accessed"),
                date_published=entry.get("date_published"),
                owner=entry.get("owner_name"),
            )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=[],
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())


class CampaignsCluster(Cluster):
    def __init__(
        self,
        authors: str,
        category: str,
        description: str,
        name: str,
        source: str,
        type: str,
        uuid: str,
    ):
        super().__init__(authors, category, description, name, source, type, uuid)

    def add_values(self, data):
        for entry in data["data"]:
            meta = CampaignsMeta(
                source=entry.get("source"),
                campaign_attack_id=entry.get("campaign_attack_id"),
                first_seen=entry.get("first_seen"),
                last_seen=entry.get("last_seen"),
                tags=[x.get("tag") for x in entry.get("tags")],
                owner=entry.get("owner_name"),
            )
            related = []
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            self.values.append(value.return_value())
