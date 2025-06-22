# Directory Structure ASCII Generator 

## dirtreegen

A lightweight Python script that generates a clean hierarchical `ASCII tree` representation of a directory structure and saves it to a text file. Automatically detects the target folder and excludes the script/output files from the listing.

## Features

- **CLI Arguments:** Specify target folder, output file, max depth, and hidden file inclusion.
- **Search:** Search for strings in files `--search`, with case control and match limits.
- **Statistics:** Detailed stats with `--stat`: directory count, file count, total size (auto-scaled).
- **Color Coding:** Matching files highlighted when using `--color`.
- **Depth Control:** Limit recursion depth with `--depth`.
- **Hidden Files:** Toggle visibility with `--include-hidden`.
- **Symlink Detection:** Detects cyclic symlinks to prevent infinite recursion.
- **Self-Exclusion:** Skips script file and output file in listings.
- **Binary File Exclusion:** Skips binary files during search to avoid timeouts.
- **Error Handling:** Gracefully handles permission issues.

## Example Output (structure.txt)
```
Directory Tree of 'your-folder-name'
Full Path: /absolute/path/to/your-folder

├── main.py
├── utils/
│   ├── helper.py
│   └── __pycache__/
└── README.md
```
## Options
```
+----------------------+---------------------------------------------+
| Flag                 | Description                                 |
+======================+=============================================+
| folder               | Target folder path (default: current dir)   |
| --output, -o         | Output file name (default: structure.txt)   |
| --depth, -d          | Max traversal depth (default: ∞)            |
| --include-hidden, -a | Show hidden files/folders                   |
| --color, -c          | Enable directory/file color coding          |
| --search, -s         | Search for STRING in file contents          |
| --case-sensitive     | Make search case-sensitive                  |
| --max-matches        | Max matches to show per file (default: 5)   |
| --stat               | Show file/directory counts and size stats   |
| --verbose, -vrb      | Show detailed progress indicator            |
| --version, -v        | Show program version                        |
+----------------------+---------------------------------------------+
```
## Usage
```bash
python dirtreegen.py [folder] [options]

# Examples:
# Generate tree for current dir with color output
python3 dirtreegen.py --color

# Search for "error" in all files, case-insensitive
python3 dirtreegen.py --search "error" --color

# Case-sensitive search for "Error" with max 2 matches
python3 dirtreegen.py -s "Æther" --case-sensitive --max-matches 2

# Scan with default settings (no color)
python3 dirtreegen.py /path/to/folder --depth 3 -o results.txt

# Show stats only
python3 dirtreegen.py --stat

# Show stats and search results
python3 dirtreegen.py --search "TODO" --stat --color

# Verbose + search + stats
python3 dirtreegen.py --search "æther" --verbose --stat --color

```
## Requirements
- Python 3.6+ (required for f-strings)
- `colorama` (v0.4.0+) for color-coded output
