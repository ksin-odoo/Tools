# Odoo Tools: Codebase Indexer & JSConfig Generator

This directory contains utility scripts to help you work efficiently with large Odoo codebases, especially for navigation, search, and editor integration.

---

## 1. codebase_indexer.py

**Purpose:**
- Indexes a set of files in your Odoo codebase for fast search, navigation, or analysis.
- Can be used to build a custom search index, tags, or to restrict search to a subset of files.

**Usage:**
```bash
python3 tools/codebase_indexer.py --file-list /path/to/file_list.txt
```
- `--file-list` should be a text file with one file path per line (relative or absolute).
- The script will process each file listed.

**Example:**
```bash
python3 tools/codebase_indexer.py --file-list /home/odoo/odoo18/pos_oder.txt
```

**Typical Use Cases:**
- Restricting search or analysis to a curated set of files.
- Building a tags or symbol index for a subset of the codebase.

---

## 2. jsconfig_generator.py

**Purpose:**
- Automatically generates a `jsconfig.json` file for VS Code (or compatible editors) to enable "Go to Definition" and IntelliSense for Odoo JS/OWL module aliases.
- Always scans both `community/addons` and `enterprise` for all modules with a `static/src` directory and creates path aliases for each.
- **Now supports any number of extra addon roots as arguments** (e.g., `team-utag`, custom vendor directories, etc.).

**Usage:**
```bash
python3 tools/jsconfig_generator.py [extra_addons_dir1] [extra_addons_dir2] ...
```
- `community/addons` and `enterprise` are always included.
- Any additional directories passed as arguments will be scanned for modules with `static/src`, and aliases will be added for those as well.

**Example (with team-utag):**
```bash
python3 tools/jsconfig_generator.py ../team-utag
```
- This will generate a `jsconfig.json` that resolves all links for community, enterprise, and all modules in `team-utag`.

**After running:**
- Reload VS Code to activate the new path aliases.
- You can now Ctrl+Click (or Cmd+Click) on any `@module_name/...` import in your JS/OWL code to jump to its definition.

**Typical Use Cases:**
- Seamless navigation and code completion in large Odoo projects.
- Supporting custom and third-party modules in your editor.
- Works for any custom addon root, not just team-utag.

---

## Prerequisites
- Python 3.x
- Run these scripts from the project root or adjust paths as needed.

---

## Customization
- To add more addon roots, simply pass them as arguments to `jsconfig_generator.py`.
- For advanced indexing, modify `codebase_indexer.py` to suit your workflow.

---

## Support
If you have questions or want to extend these tools, open an issue or contact your Odoo development team.
