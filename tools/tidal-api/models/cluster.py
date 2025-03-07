from dataclasses import dataclass, field, asdict
from typing import Type
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
class AssociatedGroupsMeta(Meta):
    id: str = None
    owner_id: str = None
    owner: str = None


@dataclass
class SoftwareMeta(Meta):
    source: str = None
    type: list = None
    software_attack_id: str = None
    platforms: list = None
    tags: list = None
    owner: str = None


@dataclass
class AssociatedSoftwareMeta(Meta):
    id: str = None
    owner_id: str = None
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
    ordinal_position: str = None
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
            k: v for k, v in asdict(self.meta).items() if v is not None and v != []
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
        self.CLUSTER_PATH = "../../clusters"

    def add_values(self, data: dict, meta_class: Type[Meta]):
        pass

    def save_to_file(self, path):
        with open(path, "w") as file:
            file.write(json.dumps(self.__dict__(), indent=2))
            file.write('\n')

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
            "version": self.version,
        }

    def _get_relation_from_mitre_id(
        self, mitre_id: str, cluster: str, meta_key: str, array: bool = False
    ):
        with open(f"{self.CLUSTER_PATH}/{cluster}.json", "r") as file:
            mitre = json.load(file)
        for entry in mitre["values"]:
            try:
                if array:
                    for id in entry["meta"][meta_key]:
                        if id == mitre_id:
                            return entry["uuid"]
                else:
                    if entry["meta"][meta_key] == mitre_id:
                        return entry["uuid"]
            except KeyError:
                continue
        return None


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
        version: int,
        enrichment: bool = False,
        subs: bool = False,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)
        self.enrichment = enrichment
        self.subs = subs

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
            if self.enrichment:
                related_cluster = self._get_relation_from_mitre_id(
                    entry.get("group_attack_id"), "threat-actor", "synonyms", True
                )
                if related_cluster:
                    related.append(
                        {
                            "dest-uuid": related_cluster,
                            "type": "similar",
                        }
                    )
            if self.subs:
                for associated_group in entry.get("associated_groups"):
                    found = False
                    for x in self.values:
                        if associated_group.get("associated_group_id") == x.get("uuid"):
                            x["related"].append(
                                {
                                    "dest-uuid": entry.get("id"),
                                    "type": "similar",
                                }
                            )
                            found = True
                            break
                    if found:
                        continue
                    associated_meta = AssociatedGroupsMeta(
                        id=associated_group.get("id"),
                        owner_id=associated_group.get("owner_id"),
                        owner=associated_group.get("owner_name"),
                    )
                    associated_related = []
                    associated_related.append(
                        {
                            "dest-uuid": entry.get("id"),
                            "type": "similar",
                        }
                    )
                    value = ClusterValue(
                        description=associated_group.get("description"),
                        meta=associated_meta,
                        related=associated_related,
                        uuid=associated_group.get("associated_group_id"),
                        value=associated_group.get("name") + " - Associated Group",
                    )
                    self.values.append(value.return_value())
                    related.append(
                        {
                            "dest-uuid": associated_group.get("associated_group_id"),
                            "type": "similar",
                        }
                    )
            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )

            # Code Block for handling duplicate from Tidal API data (hopefully only temporary)
            if value.uuid == "3290dcb9-5781-4b87-8fa0-6ae820e152cd":
                value.value = "Volt Typhoon - Tidal"

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
        version: int,
        enrichment: bool = False,
        subs: bool = False,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)
        self.enrichment = enrichment
        self.subs = subs

    def add_values(self, data):
        for entry in data["data"]:
            meta = SoftwareMeta(
                source=entry.get("source"),
                type=[entry.get("type")],
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
            if self.enrichment:
                related_cluster = self._get_relation_from_mitre_id(
                    entry.get("software_attack_id"), "mitre-tool", "external_id"
                )
                if related_cluster:
                    related.append(
                        {
                            "dest-uuid": related_cluster,
                            "type": "similar",
                        }
                    )

                related_cluster = self._get_relation_from_mitre_id(
                    entry.get("software_attack_id"), "mitre-malware", "external_id"
                )
                if related_cluster:
                    related.append(
                        {
                            "dest-uuid": related_cluster,
                            "type": "similar",
                        }
                    )
            if self.subs:
                for associated_software in entry.get("associated_software"):
                    found = False
                    for x in self.values:
                        if associated_software.get("associated_software_id") == x.get("uuid"):
                            x["related"].append(
                                {
                                    "dest-uuid": entry.get("id"),
                                    "type": "similar",
                                }
                            )
                            found = True
                            break
                    if found:
                        continue
                    associated_meta = AssociatedSoftwareMeta(
                        id=associated_software.get("id"),
                        owner_id=associated_software.get("owner_id"),
                        owner=associated_software.get("owner_name"),
                    )
                    associated_related = []
                    associated_related.append(
                        {
                            "dest-uuid": entry.get("id"),
                            "type": "similar",
                        }
                    )
                    value = ClusterValue(
                        description=associated_software.get("description"),
                        meta=associated_meta,
                        related=associated_related,
                        uuid=associated_software.get("associated_software_id"),
                        value=associated_software.get("name") + " - Associated Software",
                    )

                    self.values.append(value.return_value())
                    related.append(
                        {
                            "dest-uuid": associated_software.get(
                                "associated_software_id"
                            ),
                            "type": "similar",
                        }
                    )

            value = ClusterValue(
                description=entry.get("description"),
                meta=meta,
                related=related,
                uuid=entry.get("id"),
                value=entry.get("name"),
            )
            # duplicates, manually handled
            if value.uuid == '6af0eac2-c35f-4569-ae09-47f1ca846961':
                value.value = f"{value.value} - Duplicate"
            if value.uuid == '39d81c48-8f7c-54cb-8fac-485598e31a55':
                value.value = f"{value.value} - Duplicate"

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
        version: int,
        subs: bool = False,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)
        self.subs = subs

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

            if self.subs:
                for sub_technique in entry.get("sub_technique"):
                    sub_meta = SubTechniqueMeta(
                        source=sub_technique.get("source"),
                        technique_attack_id=sub_technique.get("technique_attack_id"),
                    )
                    sub_related = []
                    for relation in sub_technique.get("tactic"):
                        sub_related.append(
                            {
                                "dest-uuid": relation.get("tactic_id"),
                                "type": "uses",
                            }
                        )
                    sub_value = ClusterValue(
                        description=sub_technique.get("description"),
                        meta=sub_meta,
                        related=sub_related,
                        uuid=sub_technique.get("id"),
                        value=sub_technique.get("name"),
                    )

                    # Code for handling duplicate from Tidal API data (hopefully only temporary)
                    if sub_value.uuid == "be637d66-5110-4872-bc15-63b062c3f290":
                        sub_value.value = "Botnet - Duplicate"
                    elif sub_value.uuid == "5c6c3492-5dbc-43ee-a3f2-ba1976d3b379":
                        sub_value.value = "DNS - Duplicate"
                    elif sub_value.uuid == "83e4f633-67fb-4d87-b1b3-8a7a2e60778b":
                        sub_value.value = "DNS Server - Duplicate"
                    elif sub_value.uuid == "b9f5f6b7-ecff-48c8-a23e-c58fd9e41a0d":
                        sub_value.value = "Domains - Duplicate"
                    elif sub_value.uuid == "6e4a0960-dcdc-4e42-9aa1-70d6fc3677b2":
                        sub_value.value = "Server - Duplicate"
                    elif sub_value.uuid == "c30faf84-496b-4f27-a4bc-aa36d583c69f":
                        sub_value.value = "Serverless - Duplicate"
                    elif sub_value.uuid == "2c04d7c8-67a3-4b1a-bd71-47b7c5a54b23":
                        sub_value.value = "Virtual Private Server - Duplicate"
                    elif sub_value.uuid == "2e883e0d-1108-431a-a2dd-98ba98b69417":
                        sub_value.value = "Web Services - Duplicate"
                    elif sub_value.uuid == "d76c3dde-dba5-4748-8d51-c93fc34f885e":
                        sub_value.value = "Cloud Account - Duplicate"
                    elif sub_value.uuid == "12908bde-a5eb-40a5-ae27-d93960d0bfdc":
                        sub_value.value = "Domain Account - Duplicate"
                    elif sub_value.uuid == "df5f6835-ca0a-4ef5-bb3a-b011e4025545":
                        sub_value.value = "Local Account - Duplicate"
                    elif sub_value.uuid == "3c4a2f3a-5877-4a27-a417-76318523657e":
                        sub_value.value = "Cloud Accounts - Duplicate"
                    elif sub_value.uuid == "4b187604-88ab-4972-9836-90a04c705e10":
                        sub_value.value = "Cloud Accounts - Duplicate2"
                    elif sub_value.uuid == "49ae7bf1-a313-41d6-ad4c-74efc4c80ab6":
                        sub_value.value = "Email Accounts - Duplicate"
                    elif sub_value.uuid == "3426077d-3b9c-4f77-a1c6-d68f0dea670e":
                        sub_value.value = "Social Media Accounts - Duplicate"
                    elif sub_value.uuid == "fe595943-f264-4d05-a8c7-7afc8985bfc3":
                        sub_value.value = "Code Repositories - Duplicate"
                    elif sub_value.uuid == "2735f8d1-0e46-4cd7-bfbb-78941bb266fd":
                        sub_value.value = "Steganography - Duplicate"
                    elif sub_value.uuid == "6f152555-36a5-4ec9-8b9b-f0b32c3ccef8":
                        sub_value.value = "Code Signing Certificates - Duplicate"
                    elif sub_value.uuid == "5bcbb0c5-7061-481f-a677-09028a6c59f7":
                        sub_value.value = "Digital Certificates - Duplicate"
                    elif sub_value.uuid == "4c0db4e5-14e0-4fb7-88b0-bb391ce5ad58":
                        sub_value.value = "Digital Certificates - Duplicate2"
                    elif sub_value.uuid == "5a57d258-0b23-431b-b50e-3150d2c0e52c":
                        sub_value.value = "Exploits - Duplicate"
                    elif sub_value.uuid == "0f77a14a-d450-4885-b81f-23eeffa53a7e":
                        sub_value.value = "Malware - Duplicate"
                    elif sub_value.uuid == "ba553ad4-5699-4458-ae4e-76e1faa43291":
                        sub_value.value = "Spearphishing Attachment - Duplicate"
                    elif sub_value.uuid == "d08a9977-9fc2-46bb-84f9-dbb5187c426d":
                        sub_value.value = "Spearphishing Link - Duplicate"
                    elif sub_value.uuid == "350c12a3-33f6-5942-8892-4d6e70abbfc1":
                        sub_value.value = "Spearphishing Voice - Duplicate"

                    self.values.append(sub_value.return_value())
                    related.append(
                        {
                            "dest-uuid": sub_technique.get("id"),
                            "type": "similar",
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
        version: int,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)

    def add_values(self, data):
        for entry in data["data"]:
            meta = TacticMeta(
                source=entry.get("source"),
                tactic_attack_id=entry.get("tactic_attack_id"),
                ordinal_position=str(entry.get("ordinal_position")),
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
        version: int,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)

    def add_values(self, data):
        for entry in data["data"]:
            meta = ReferencesMeta(
                source=entry.get("source"),
                refs=[entry.get("url")] if entry.get("url") != "" else None,
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

            # handle duplicates manually
            if value.uuid == 'eea178f4-80bd-49d1-84b1-f80671e9a3e4':
                value.value = f"{value.value} - Duplicate"
            if value.uuid == '9bb5c330-56bd-47e7-8414-729d8e6cb3b3':
                value.value = f"{value.value} - Duplicate"
            if value.uuid == '8b4bdce9-da19-443f-88d2-11466e126c09':
                value.value = f"{value.value} - Duplicate"
            if value.uuid == 'b4727044-51bb-43b3-afdb-515bb4bb0f7e':
                value.value = f"{value.value} - Duplicate"

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
        version: int,
    ):
        super().__init__(authors, category, description, name, source, type, uuid, version)

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
