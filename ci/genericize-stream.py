#!/usr/bin/python3

import argparse
import json
import sys

def walk(item, cb_obj=None, cb_list=None, cb_str=None):
    '''Recursively descend a JSON dict, calling callbacks for each type.
    cb_str() must return the replacement string.'''
    if isinstance(item, dict):
        ret = {}
        for k, v in item.items():
            ret[k] = walk(v, cb_obj, cb_list, cb_str)
        if cb_obj:
            cb_obj(ret)
        return ret
    elif isinstance(item, list):
        ret = []
        for v in item:
            ret.append(walk(v, cb_obj, cb_list, cb_str))
        if cb_list:
            cb_list(ret)
        return ret
    elif isinstance(item, str):
        if cb_str:
            item = cb_str(item)
        return item
    else:
        return item


def replace_string(tree, old, new):
    '''Replace substring old with new throughout tree.'''
    return walk(tree, cb_str=lambda s: s.replace(old, new))


def replace_key(tree, key, new):
    '''Replace the value of key with new throughout tree.'''
    def cb_obj(o):
        if key in o:
            o[key] = new
    return walk(tree, cb_obj=cb_obj)


def get_releases(stream):
    '''Get all releases mentioned in the stream metadata.'''
    releases = set()
    def cb_obj(obj):
        release = obj.get('release', None)
        if release:
            releases.add(release)
    walk(stream, cb_obj=cb_obj)
    return releases


def genericize_stream(path):
    '''Load the stream metadata at path and remove all version-specific
    references.'''
    with open(path) as f:
        input = f.read()

    stream = json.loads(input)
    stream['metadata']['last-modified'] = 'LAST-MODIFIED'
    stream = replace_key(stream, 'sha256', 'HASH')
    stream = replace_key(stream, 'uncompressed-sha256', 'HASH')
    for release in get_releases(stream):
        stream = replace_string(stream, release, 'RELEASE')
        # for GCP image name
        stream = replace_string(stream, release.replace('.', '-'), 'RELEASE')
    # replace AMI IDs
    for arch in stream['architectures'].values():
        aws = arch.get('images', {}).get('aws', {})
        aws['regions'] = replace_key(aws.get('regions', {}), 'image', 'AMI')
    output = json.dumps(stream, indent=4)

    if len(input.splitlines()) != len(output.splitlines()):
        # This could make the interdiff annotations appear on the wrong lines,
        # and shouldn't happen provided that the input data is
        # pretty-printed, so fail.
        raise Exception('Genericizing stream metadata changed the line count')
    return output


def main():
    parser = argparse.ArgumentParser(
            description='Remove release-specific items from stream metadata.')
    parser.add_argument('path',
            help='path to stream metadata')
    args = parser.parse_args()

    print(genericize_stream(args.path))


if __name__ == '__main__':
    main()
