# Note: In the future, it would be more efficient to use a schema for validation.
# This approach can simplify the validation process and ensure consistency.

#!/usr/bin/python3

import argparse
import yaml
import re
import sys

def validate_release_notes_structure(data):
    valid = True

    if not isinstance(data, dict):
        print("Error: YAML root should be a dictionary.")
        valid = False

    if 'releases' not in data:
        print("Error: 'releases' key not found.")
        valid = False

    if not isinstance(data.get('releases'), dict):
        print("Error: 'releases' key should contain a dictionary.")
        valid = False

    for release, content in data.get('releases', {}).items():
        if not re.match(r'^\d+\.\d{8}\.\d+\.\d+$', release):
            print(f"Error: Release key '{release}' should follow the pattern 'x.yyyymmdd.n.m'.")
            valid = False

        if not isinstance(content, dict):
            print(f"Error: Release {release} should contain a dictionary.")
            valid = False

        if 'issues' not in content:
            print(f"Error: 'issues' key not found for release {release}.")
            valid = False

        if not isinstance(content.get('issues'), list):
            print(f"Error: 'issues' key for release {release} should contain a list.")
            valid = False

        for issue in content.get('issues', []):
            if not isinstance(issue, dict):
                print(f"Error: Each issue for release {release} should be a dictionary.")
                valid = False

            if 'text' not in issue:
                print(f"Error: 'text' key not found in issue for release {release}.")
                valid = False
            if 'url' not in issue:
                print(f"Error: 'url' key not found in issue for release {release}.")
                valid = False

    return valid

def main():
    parser = argparse.ArgumentParser(description='Validate release notes YAML files.')
    parser.add_argument('paths', nargs='+', help='paths to YAML files')
    args = parser.parse_args()

    all_valid = True

    for yaml_file in args.paths:
        print(f"Validating {yaml_file}...")

        try:
            with open(yaml_file, 'r') as file:
                data = yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading YAML file: {e}")
            all_valid = False
            continue

        if not validate_release_notes_structure(data):
            all_valid = False

    if all_valid:
        print("Validation successful for all files.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
