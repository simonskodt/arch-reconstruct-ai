"""Parse the toml dependencies in order to check whether these packages are outdated"""
#!/usr/bin/env python3
import re
import tomllib  # use `import tomli` if Python <3.11
PYPROJECT_PATH ="pyproject.toml"

with open(PYPROJECT_PATH, "rb") as f:
    data = tomllib.load(f)

dependencies = data.get("project", {}).get("dependencies", [])
names = []
for dep in dependencies:
    dep = dep.strip().lstrip('\'"').rstrip('\'"')  # remove surrounding quotes
    dep = dep.split("[", 1)[0]  # drop extras
    # split at first whitespace or version/operator char (<,>,=,!,~,;) and take the left part
    name = re.split(r'[\s<>=!~;]', dep, maxsplit=1)[0]
    if name:
        names.append(name.lower())
print(names)
