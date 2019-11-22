import pandas as pd
import os
import json
import uuid
import xlrd


class Amitt:
    """
    Create MISP galaxy and cluster JSON files.

    This script relies on the AMITT metadata xlsx available here:
    https://github.com/misinfosecproject/amitt_framework/blob/master/generating_code/amitt_metadata_v3.xlsx

    This script has been adapted from:
    https://github.com/misinfosecproject/amitt_framework/blob/master/generating_code/amitt.py
    """

    def __init__(self, infile='amitt_metadata_v3.xlsx'):
        metadata = {}
        xlsx = pd.ExcelFile(infile)
        for sheetname in xlsx.sheet_names:
            metadata[sheetname] = xlsx.parse(sheetname)

        # Create individual tables and dictionaries
        self.phases = metadata['phases']
        self.techniques = metadata['techniques']
        self.tasks = metadata['tasks']
        self.incidents = metadata['incidents']

        tactechs = self.techniques.groupby('tactic')['id'].apply(list).reset_index().rename({'id': 'techniques'},
                                                                                            axis=1)
        self.tactics = metadata['tactics'].merge(tactechs, left_on='id', right_on='tactic', how='left').fillna('').drop(
            'tactic', axis=1)

        self.tacdict = self.make_object_dict(self.tactics)

    def make_object_dict(self, df):
        return pd.Series(df.name.values, index=df.id).to_dict()

    def make_amitt_galaxy(self):
        galaxy = {}
        galaxy['name'] = 'Misinformation Pattern'
        galaxy['type'] = 'amitt-misinformation-pattern'
        galaxy['description'] = 'AM!TT Tactic'
        galaxy['uuid'] = str(uuid.uuid4())
        galaxy['version'] = 3
        galaxy['icon'] = 'map'
        galaxy['namespace'] = 'misinfosec'

        galaxy['kill_chain_order'] = {
            'misinformation-tactics': []
        }

        for k, v in self.tacdict.items():
            galaxy['kill_chain_order']['misinformation-tactics'].append(v)

        return galaxy

    def write_amitt_file(self, fname, file_data):
        with open(fname, 'w') as f:
            json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')

    def make_amitt_cluster(self):
        cluster = {}
        cluster['authors'] = ['misinfosecproject']
        cluster['category'] = 'misinformation-pattern'
        cluster['description'] = 'AM!TT Technique'
        cluster['name'] = 'Misinformation Pattern'
        cluster['source'] = 'https://github.com/misinfosecproject/amitt_framework'
        cluster['type'] = 'amitt-misinformation-pattern'
        cluster['uuid'] = str(uuid.uuid4())
        cluster['values'] = []
        cluster['version'] = 3

        techniques = self.techniques.values.tolist()

        for technique in techniques:
            t = {}

            if technique[1] != technique[1]:
                technique[1] = ''

            if technique[2] != technique[2]:
                technique[2] = ''

            if technique[3] != technique[3]:
                technique[3] = ''

            if technique[1] == technique[2] == technique[3] == '':
                continue

            t['uuid'] = str(uuid.uuid4())
            t['value'] = technique[1]
            t['description'] = technique[3]
            t['meta'] = {
                'external_id': technique[0],
                'kill_chain': [
                    'misinfosec:misinformation-tactics:' + self.tacdict[technique[2]].replace(' ', '-').lower()
                ],
                'refs': [
                    'https://github.com/misinfosecproject/amitt_framework/blob/master/techniques/' + technique[
                        0] + '.md'
                ]
            }

            cluster['values'].append(t)

        return cluster

    def make_amitt_task_cluster(self):
        cluster = {}
        cluster['authors'] = ['misinfosecproject']
        cluster['category'] = 'misinformation-pattern'
        cluster['description'] = 'AM!TT Task'
        cluster['name'] = 'Misinformation Task'
        cluster['source'] = 'https://github.com/misinfosecproject/amitt_framework'
        cluster['type'] = 'amitt-misinformation-pattern'
        cluster['uuid'] = str(uuid.uuid4())
        cluster['values'] = []
        cluster['version'] = '3'

        techniques = self.techniques.values.tolist()

        for technique in techniques:
            t = {}

            if technique[1] != technique[1]:
                technique[1] = ''

            if technique[2] != technique[2]:
                technique[2] = ''

            if technique[3] != technique[3]:
                technique[3] = ''

            if technique[1] == technique[2] == technique[3] == '':
                continue

            t['uuid'] = str(uuid.uuid4())
            t['value'] = technique[1]
            t['description'] = technique[3]
            t['meta'] = {
                'external_id': technique[0],
                'kill_chain': [
                    'misinfosec:misinformation-tactics:' + self.tacdict[technique[2]].replace(' ', '-').lower()
                ],
                'refs': [
                    'https://github.com/misinfosecproject/amitt_framework/blob/master/techniques/' + technique[
                        0] + '.md'
                ]
            }

            cluster['values'].append(t)

        return cluster


def main():
    amitt = Amitt()

    galaxy = amitt.make_amitt_galaxy()
    amitt.write_amitt_file('../galaxies/misinfosec-amitt-misinformation-pattern.json', galaxy)

    cluster = amitt.make_amitt_cluster()
    amitt.write_amitt_file('../clusters/misinfosec-amitt-misinformation-pattern.json', cluster)


if __name__ == '__main__':
    main()
