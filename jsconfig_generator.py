import os
import json
import sys

"""
Usage:
    python3 jsconfig_generator.py [extra_addons_dir1] [extra_addons_dir2] ...

- Always includes community/addons and enterprise as permanent roots.
- Any additional directories passed as arguments will be scanned for modules with static/src, and aliases will be added for those as well.
"""

COMMUNITY_ADDONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../community/addons")
)
ENTERPRISE_ADDONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../enterprise")
)
JSCONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../jsconfig.json")
)

aliases = {}

# Scan community addons
for module in os.listdir(COMMUNITY_ADDONS_DIR):
    module_path = os.path.join(COMMUNITY_ADDONS_DIR, module)
    static_src = os.path.join(module_path, "static", "src")
    if os.path.isdir(static_src):
        aliases[f"@{module}/*"] = [f"community/addons/{module}/static/src/*"]

# Scan enterprise addons
for module in os.listdir(ENTERPRISE_ADDONS_DIR):
    module_path = os.path.join(ENTERPRISE_ADDONS_DIR, module)
    static_src = os.path.join(module_path, "static", "src")
    if os.path.isdir(static_src):
        aliases[f"@{module}/*"] = [f"enterprise/{module}/static/src/*"]

# Scan any extra addon roots passed as arguments
for extra_dir in sys.argv[1:]:
    extra_dir = os.path.abspath(extra_dir)
    if not os.path.isdir(extra_dir):
        print(f"Warning: {extra_dir} is not a directory, skipping.")
        continue
    for module in os.listdir(extra_dir):
        module_path = os.path.join(extra_dir, module)
        static_src = os.path.join(module_path, "static", "src")
        if os.path.isdir(static_src):
            # Use the relative path for VS Code
            rel_path = os.path.relpath(
                static_src, os.path.dirname(JSCONFIG_PATH)
            ).replace("static/src", "static/src/*")
            aliases[f"@{module}/*"] = [
                f"{os.path.relpath(module_path, os.path.dirname(JSCONFIG_PATH))}/static/src/*"
            ]

jsconfig = {
    "compilerOptions": {"baseUrl": ".", "paths": aliases},
    "include": ["community/addons/**/*", "enterprise/**/*"]
    + [
        os.path.join(os.path.relpath(arg, os.path.dirname(JSCONFIG_PATH)), "**/*")
        for arg in sys.argv[1:]
    ],
    "exclude": ["node_modules"],
}

with open(JSCONFIG_PATH, "w") as f:
    json.dump(jsconfig, f, indent=2)

print(
    f"jsconfig.json generated with {len(aliases)} aliases (community + enterprise + {len(sys.argv[1:])} custom roots)."
)
