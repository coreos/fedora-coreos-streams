#!/usr/bin/python3

import argparse
import yaml
import re
import sys

def validate_release_notes_structure(data, file_name):
    if not isinstance(data, dict):
        print(f"Error: YAML root should be a dictionary in {file_name}.")
        return False

    if 'releases' not in data:
        print(f"Error: 'releases' key not found in {file_name}.")
        return False

    if not isinstance(data['releases'], dict):
        print(f"Error: 'releases' key should contain a dictionary in {file_name}.")
        return False

    for release, content in data['releases'].items():
        if not re.match(r'^\d+\.\d{8}\.\d+\.\d+$', release):
            print(f"Error: Release key '{release}' should follow the pattern 'x.yyyymmdd.n.m' in {file_name}.")
            return False
        
        release_line = f"{release}:"
        if not release_line.endswith(':'):
            print(f"Error: Release key '{release}' does not end with a colon ':' in {file_name}.")
            return False

        if not isinstance(content, dict):
            print(f"Error: Release {release} should contain a dictionary in {file_name}.")
            return False

        if 'issues' not in content:
            print(f"Error: 'issues' key not found for release {release} in {file_name}.")
            return False

        if not isinstance(content['issues'], list):
            print(f"Error: 'issues' key for release {release} should contain a list in {file_name}.")
            return False

        for issue in content['issues']:
            if not isinstance(issue, dict):
                print(f"Error: Each issue for release {release} should be a dictionary in {file_name}.")
                return False

            if 'text' not in issue:
                print(f"Error: 'text' key not found in issue for release {release} in {file_name}.")
                return False
            if 'url' not in issue:
                print(f"Error: 'url' key not found in issue for release {release} in {file_name}.")
                return False

    return True

def validate_indentation(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    indent_size = 2
    for i, line in enumerate(lines):
        stripped_line = line.lstrip()
        if stripped_line and (len(line) - len(stripped_line)) % indent_size != 0:
            print(f"Error: Incorrect indentation at line {i + 1} in {file_path}: '{line.strip()}'")
            return False
    return True

def main():
    parser = argparse.ArgumentParser(description='Validate release notes YAML files.')
    parser.add_argument('path', help='path to release notes yaml file')
    args = parser.parse_args()

    yaml_file = args.path
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file {yaml_file}: {e}")
        sys.exit(1)

    if not validate_release_notes_structure(data, yaml_file):
        sys.exit(1)

    if not validate_indentation(yaml_file):
        sys.exit(1)

    print(f"Validation successful for {yaml_file}.")

if __name__ == "__main__":
    main()
