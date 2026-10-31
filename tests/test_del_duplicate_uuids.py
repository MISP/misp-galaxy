#!/usr/bin/env python3
# coding=utf-8
"""
    Tests for tools/del_duplicate_uuids.py
"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / 'tools' / 'del_duplicate_uuids.py'


def write_cluster(path, uuids, version=3):
    data = {
        'name': 'Test cluster',
        'type': 'test',
        'uuid': '9b8b0d0a-1b7e-4a8f-9c7f-0d5a6b7c8d9e',
        'description': 'Test cluster',
        'version': version,
        'values': [{'value': f'value-{i}', 'uuid': u} for i, u in enumerate(uuids)],
    }
    with open(path, 'w') as f:
        json.dump(data, f)
    return data


def run(path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def test_version_incremented_when_duplicate_removed(tmp_path):
    path = tmp_path / 'cluster.json'
    dup = '11111111-1111-1111-1111-111111111111'
    write_cluster(path, [dup, '22222222-2222-2222-2222-222222222222', dup], version=3)

    assert run(path).returncode == 0

    with open(path) as f:
        result = json.load(f)
    assert len(result['values']) == 2
    assert result['version'] == 4


def test_file_untouched_when_no_duplicate(tmp_path):
    path = tmp_path / 'cluster.json'
    write_cluster(path, ['11111111-1111-1111-1111-111111111111',
                         '22222222-2222-2222-2222-222222222222'], version=3)
    before = path.read_bytes()

    assert run(path).returncode == 0

    assert path.read_bytes() == before
    with open(path) as f:
        assert json.load(f)['version'] == 3
