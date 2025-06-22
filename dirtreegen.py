#!/usr/bin/env python3
import os
import sys
import argparse
import shutil
from colorama import Fore, Style, init

__version__ = "1.0"

# Check Python version (requires 3.6+ for f-strings)
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or newer")
    print("f-strings require Python 3.6+")
    sys.exit(1)

# Check colorama version
try:
    import colorama
    from colorama import Fore, Style, init
except ImportError:
    print(f"{Fore.RED}Error: 'colorama' module not found")
    print("Install it via: pip install colorama")
    sys.exit(1)

def main():
    init(autoreset=True)

    BINARY_EXTENSIONS = {
        '.pyc', '.exe', '.dll', '.so', '.o', '.a', '.lib', '.pdb',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
        '.mp3', '.wav', '.ogg', '.flac', '.mp4', '.avi', '.mkv',
        '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
        '.pdf', '.docx', '.xlsx', '.pptx'
    }

    parser = argparse.ArgumentParser(description=f"Generate ASCII tree of directory structure (v{__version__})")
    parser.add_argument("folder", nargs="?", help="Target folder path (default: current directory)")
    parser.add_argument("--output", "-o", default="structure.txt", help="Output file name")
    parser.add_argument("--depth", "-d", type=int, default=None, help="Maximum depth to traverse")
    parser.add_argument("--include-hidden", "-a", action="store_true", help="Include hidden files/folders")
    parser.add_argument("--color", "-c", action="store_true", help="Enable directory/file color coding (blue for directories, green for files)")
    parser.add_argument("--search", "-s", type=str, metavar='STRING', help="Search for STRING in file contents (case-insensitive)")
    parser.add_argument("--case-sensitive", action="store_true", help="Make search case-sensitive")
    parser.add_argument("--max-matches", type=int, default=5, help="Maximum number of matches to show per file (default: 5)")
    parser.add_argument("--stat", action="store_true", help="Show file/directory counts and size statistics")
    parser.add_argument("--verbose", "-vrb", action="store_true", help="Show detailed progress indicator")
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s v{__version__}", help="Show program version")
    args = parser.parse_args()

    # Determine target folder
    if args.folder:
        TARGET_FOLDER = os.path.abspath(args.folder)
    else:
        TARGET_FOLDER = os.getcwd()

    # Global exclusions
    script_name = os.path.basename(sys.argv[0])
    output_basename = os.path.basename(args.output)

    def format_size(size_bytes):
        """Convert bytes to human-readable format (KB, MB, GB)"""
        if size_bytes == 0:
            return "0 B"
        size = size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def generate_tree_entries(path, prefix="", current_depth=0, visited=None):
        """Recursively generate tree entries with metadata"""
        if visited is None:
            visited = set()

        path = os.path.abspath(path)
        entries = []

        if path in visited:
            entries.append({
                "line": prefix + "! CYCLIC SYMLINK",
                "is_dir": False,
                "path": None,
                "matches": ["! SKIPPED: Cyclic symlink"]
            })
            return entries

        visited.add(path)

        try:
            # Verbose scanning output
            if args.verbose:
                terminal_width = shutil.get_terminal_size((80, 20)).columns
                path_display = path if len(path) < terminal_width - 10 else "..." + path[-(terminal_width - 13):]
                print(f"{Style.DIM}Scanning: {path_display}{Style.RESET_ALL}{' ' * (terminal_width - len(path_display) - 9)}", end="\r", flush=True)

            with os.scandir(path) as scandir_it:
                valid_entries = [
                    entry for entry in scandir_it
                    if (args.include_hidden or not entry.name.startswith('.')) and
                       entry.name not in (script_name, output_basename)
                ]
                valid_entries.sort(key=lambda e: (not e.is_dir(), e.name))

                for i, entry in enumerate(valid_entries):
                    connector = "└── " if i == len(valid_entries) - 1 else "├── "
                    entry_prefix = prefix + connector

                    is_dir = entry.is_dir()
                    entry_path = entry.path

                    if is_dir:  # Use the boolean we already computed
                        entry_line = entry_prefix + entry.name + "/"
                    else:
                        entry_line = entry_prefix + entry.name

                    # File search logic
                    matches = []
                    if not is_dir and args.search:
                        _, ext = os.path.splitext(entry.name)
                        if ext.lower() in BINARY_EXTENSIONS:
                            matches.append("! SKIPPED: Binary file")
                        else:
                            try:
                                match_count = 0
                                with open(entry_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    for line_num, line in enumerate(f, 1):
                                        if args.case_sensitive:
                                            if args.search in line:
                                                matches.append(f"Line {line_num}: {line.strip()}")
                                                match_count += 1
                                        else:
                                            if args.search.lower() in line.lower():
                                                matches.append(f"Line {line_num}: {line.strip()}")
                                                match_count += 1

                                        if match_count >= args.max_matches:
                                            matches.append(f"+ {match_count - args.max_matches} more matches")
                                            break
                            except Exception as e:
                                matches.append(f"! ERROR: {str(e)}")

                    # Add entry with matches
                    entries.append({
                        "line": entry_line,
                        "is_dir": is_dir,
                        "path": entry_path,
                        "matches": matches
                    })

                    # Recursive directory handling
                    if is_dir and (args.depth is None or current_depth < args.depth):
                        new_prefix = prefix + ("    " if i == len(valid_entries) - 1 else "│   ")
                        subdir_entries = generate_tree_entries(entry_path, new_prefix, current_depth + 1, visited)
                        entries.extend(subdir_entries)

        except PermissionError:
            entries.append({
                "line": prefix + "! PERMISSION DENIED",
                "is_dir": False,
                "path": None,
                "matches": []
            })
        except Exception as e:
            entries.append({
                "line": prefix + f"! ERROR: {str(e)}",
                "is_dir": False,
                "path": None,
                "matches": []
            })

        return entries

    # Validate target folder
    if not os.path.isdir(TARGET_FOLDER):
        print(f"{Fore.RED}Error: '{TARGET_FOLDER}' is not a valid directory")
        sys.exit(1)

    # Generate tree entries
    tree_entries = generate_tree_entries(TARGET_FOLDER)

    # Statistics Collection
    if args.stat:
        files = 0
        dirs = 0
        total_size = 0
        matching_files = 0
        total_matches = 0

        for entry in tree_entries:
            if entry["is_dir"]:
                dirs += 1
            else:
                files += 1
                try:
                    total_size += os.path.getsize(entry["path"])
                except (PermissionError, OSError):
                    pass

        if args.search:
            for entry in tree_entries:
                if not entry["is_dir"] and "matches" in entry:
                    valid_matches = [m for m in entry["matches"] if not m.startswith("! SKIPPED")]
                    if valid_matches:
                        matching_files += 1
                        total_matches += len(valid_matches)

    # Clear progress line (only if verbose)
    if args.verbose:
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        print(" " * terminal_width, end="\r")

    # Write output file
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"Directory Tree of '{os.path.basename(TARGET_FOLDER)}'\n")
            f.write(f"Full Path: {TARGET_FOLDER}\n\n")

            for entry in tree_entries:
                f.write(entry["line"] + "\n")
                if args.search and entry.get("matches") and not entry["is_dir"]:
                    for match in entry["matches"]:
                        if not match.startswith("! SKIPPED"):
                            f.write(f"    └── {match}\n")
                                    
    except Exception as e:
        print(f"{Fore.RED}File write error: {str(e)}")

    # Console output with matches (default: GREEN)
    print(f"\n{Fore.GREEN}Directory Tree Preview:\n{Fore.GREEN}{'=' * 69}")
    for entry in tree_entries:
        color = Fore.GREEN if entry["is_dir"] else Fore.GREEN
        has_matches = not entry["is_dir"] and entry.get("matches") and not entry["matches"][0].startswith("! SKIPPED")

        if getattr(args, 'color', False) and has_matches:
            color = Fore.YELLOW  # Highlight matching files

        print(color + entry["line"])

        if args.search and has_matches:
            for match in entry["matches"]:
                if match.startswith("+"):
                    print(f"{Fore.RED}    └── {match}")
                elif not match.startswith("! SKIPPED"):
                    print(f"{Fore.CYAN}    └── {match}")

    print(Fore.GREEN + '=' * 69 + "\n")

    # Print statistics # print(f"{Fore.GREEN}♪♫•*¨*•.🌣.•*¨*•♫♪")
    print(f"\n{Style.BRIGHT}{Fore.GREEN}Statistics Summary:")
    print(Fore.GREEN + '=' * 20 + "\n")
    print(f"{Fore.GREEN}Directories:   {dirs}")
    print(f"{Fore.GREEN}Files:         {files} (Total Size: {format_size(total_size)})")
    if args.search:
        print(f"Search Hits:   {matching_files} files ({total_matches} matches)")
    
    
    # Print save path
    print(f"\n{Style.BRIGHT}{Fore.GREEN}Tree saved to: {os.path.join(TARGET_FOLDER, args.output)}")
    print(Style.RESET_ALL)

if __name__ == "__main__":
    main()
