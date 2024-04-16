#!/usr/bin/env python
import glob
import re
import os
import sys


class Role():
    def __init__(self, role_dir):
        self.dir = role_dir
        self.name = os.path.basename(role_dir)

    def read_vars_from_tasks(self):
        task_files = glob.glob(f"{self.dir}/tasks/*.yml")
        variable_names = set()
        for task_file in task_files:
            with open(task_file, 'r') as f:
                for line in f:
                    matches = re.findall(f'({self.name}_[\w]+)', line)
                    for match in matches:
                        variable_names.add(match)

        return self._group_variables(variable_names)

    def _group_variables(self, variable_names):
        groups = dict()
        for variable in variable_names:
            if variable in [
                    f"{self.name}_hostname",
                    f"{self.name}_username",
                    f"{self.name}_password",
                    f"{self.name}_port",
                    f"{self.name}_validate_certs"
                    ]:
                try:
                    groups['auth'].add(variable)
                except KeyError:
                    groups['auth'] = set([variable])
                continue
            if variable in [
                    f"{self.name}_cluster",
                    f"{self.name}_cluster_name",
                    f"{self.name}_datacenter",
                    f"{self.name}_datacenter_name",
                    f"{self.name}_folder"
                    ]:
                try:
                    groups['placement'].add(variable)
                except KeyError:
                    groups['placement'] = set([variable])
                continue

            try:
                groups['other'].add(variable)
            except KeyError:
                groups['other'] = set([variable])

        return groups

    def read_default_values(self):
        default_values = dict()
        try:
            with open(f"{self.dir}/defaults/main.yml") as f:
                for line in f:
                    if line.startswith('---'):
                        continue
                    _split = line.split(': ')
                    default_values[_split[0]] = _split[1]
        except (FileExistsError, FileNotFoundError):
            pass

        return default_values


def format_for_readme(variables, default_values):
    print()
    for group in variables.keys():
        print(f"### {group.capitalize()}")
        for variable in variables[group]:
            print(f"- **{variable}**:")
            print(f"  - enter your description here")
            try:
                print(f"  - Default value is '{default_values[variable]}'")
            except KeyError:
                print()


def main():
    if len(sys.argv) != 2:
        print('\nERROR: This script requires one argument, the path to the role you want to scan for variables\n')
        sys.exit()
    role = Role(sys.argv[1].strip('/'))
    format_for_readme(role.read_vars_from_tasks(), role.read_default_values())


if __name__ == '__main__':
    main()

