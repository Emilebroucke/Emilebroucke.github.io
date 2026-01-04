# Project scaffolder

The `project_scaffolder.py` script creates a ready-to-use folder structure for a new project. You can download the file directly and run it with Python.

## Quick start

```bash
python project_scaffolder.py
```

When run without arguments, the script will prompt for a project name and create a new directory with a set of common subfolders (for example `src`, `tests`, and `public/images`). The new project directory is created inside the current working directory.

### Command-line options

- `project_name` (positional): provide the name up front to skip the prompt.
- `-o, --output-dir PATH`: choose where the project directory is created. Defaults to the current directory.
- `-s, --structure-file FILE`: path to a JSON file containing a list of folders, or a dictionary with a top-level `folders` list, to override the defaults.
- `-f, --force`: allow using an existing non-empty project directory. Existing contents are preserved.

### Custom structure example

Save the following as `custom.json` and pass it via `--structure-file custom.json`:

```json
{
  "folders": [
    "api",
    "client",
    "client/components",
    "client/styles",
    "infrastructure",
    "infra/pulumi"
  ]
}
```
