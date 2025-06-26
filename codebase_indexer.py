#!/usr/bin/env python3
"""
Codebase Indexer - A tool for creating LLM-friendly codebase indexes
"""

import fnmatch
import subprocess
from pathlib import Path
from typing import List, Set, Optional
import argparse

# Language detection mapping
LANGUAGE_MAP = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    ".pxd": "python",
    ".pxi": "python",
    ".pyd": "python",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    # XML
    ".xml": "xml",
    ".xhtml": "xml",
    # Shell
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    # Configuration
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    # Documentation
    ".md": "markdown",
    ".rst": "rst",
    ".txt": "text",
    # SQL
    ".sql": "sql",
    # C/C++
    ".c": "c",
    ".cpp": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    # Java
    ".java": "java",
    ".class": "java",
    # Ruby
    ".rb": "ruby",
    ".rbw": "ruby",
    # PHP
    ".php": "php",
    ".phtml": "php",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Swift
    ".swift": "swift",
    # Kotlin
    ".kt": "kotlin",
    ".kts": "kotlin",
}

# Common directories to exclude
DEFAULT_EXCLUDES = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "target",
    "venv",
    ".env",
    ".idea",
    ".vscode",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dylib",
    "*.dll",
    "*.class",
    "*.o",
    "*.a",
    "*.lib",
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "*.log",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "*.bak",
    "*.backup",
    "*.orig",
    "*.rej",
    "*.patch",
    "*.diff",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.rar",
    "*.7z",
    "*.bz2",
    "*.xz",
    "*.tgz",
    "*.tar.gz",
    "*.tar.bz2",
    "*.tar.xz",
}


class CodebaseIndexer:
    def __init__(
        self, root_dir: str, output_file: str, excludes: Optional[Set[str]] = None
    ):
        self.root_dir = Path(root_dir).resolve()
        self.output_file = Path(output_file).resolve()
        self.excludes = set(DEFAULT_EXCLUDES)
        if excludes:
            self.excludes.update(excludes)

        # Load .gitignore patterns if exists
        self.gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = self.root_dir / ".gitignore"
        if not gitignore_path.exists():
            return []

        patterns = []
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        return patterns

    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns."""
        # Check against default excludes
        for pattern in self.excludes:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if pattern in str(path):
                return True

        # Check against .gitignore patterns
        for pattern in self.gitignore_patterns:
            if fnmatch.fnmatch(str(path), pattern):
                return True

        return False

    def _get_language(self, path: Path) -> str:
        """Determine the language for syntax highlighting."""
        ext = path.suffix.lower()
        return LANGUAGE_MAP.get(ext, "text")

    def _generate_tree(self) -> str:
        """Generate a directory tree using the 'tree' command if available."""
        try:
            # Try to use the tree command
            result = subprocess.run(
                ["tree", "-a", "-I", "|".join(self.excludes), str(self.root_dir)],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to manual tree generation
            return self._manual_tree_generation()

    def _manual_tree_generation(self) -> str:
        """Generate a directory tree manually if 'tree' command is not available."""
        tree = []

        def _walk_dir(path: Path, prefix: str = "", is_last: bool = True):
            if self._should_exclude(path):
                return

            # Add current directory/file
            tree.append(f"{prefix}{'└── ' if is_last else '├── '}{path.name}")

            if path.is_dir():
                # Get all items in directory
                items = sorted(path.iterdir())
                # Filter out excluded items
                items = [item for item in items if not self._should_exclude(item)]

                # Process each item
                for i, item in enumerate(items):
                    is_last_item = i == len(items) - 1
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    _walk_dir(item, new_prefix, is_last_item)

        _walk_dir(self.root_dir)
        return "\n".join(tree)

    def _process_file(self, path: Path) -> str:
        """Process a single file and return its formatted content."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Skip binary files
            return ""

        # Get relative path from root
        rel_path = path.relative_to(self.root_dir)
        language = self._get_language(path)

        # Format the content
        return f"**{rel_path}**\n\n```{language}\n{content}\n```\n\n"

    def index(self):
        """Create the codebase index."""
        print(f"Indexing codebase in {self.root_dir}...")

        # Create output file
        with open(self.output_file, "w", encoding="utf-8") as f:
            # Write header
            f.write("# Codebase Index\n\n")

            # Write directory tree
            f.write("## Directory Structure\n\n")
            f.write("```\n")
            f.write(self._generate_tree())
            f.write("\n```\n\n")

            # Write file contents
            f.write("## File Contents\n\n")

            # Process all files
            for path in self.root_dir.rglob("*"):
                if path.is_file() and not self._should_exclude(path):
                    content = self._process_file(path)
                    if content:  # Skip empty content (e.g., binary files)
                        f.write(content)

        print(f"Index created successfully at {self.output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Create an LLM-friendly index of a codebase"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory to index (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="codebase_index.md",
        help="Output file path (default: codebase_index.md)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        help="Additional patterns to exclude (can be used multiple times)",
    )
    parser.add_argument(
        "--simple-list",
        action="store_true",
        help="Output a simple list of all files and folders (one per line, relative to root)",
    )
    parser.add_argument(
        "--input-list",
        type=str,
        help="Path to a file containing a list of files/folders to index (one per line, relative to root_dir)",
    )

    args = parser.parse_args()

    excludes = set(args.exclude) if args.exclude else None
    indexer = CodebaseIndexer(args.root_dir, args.output, excludes)

    # If input-list is provided, read the list of paths
    input_paths = None
    if args.input_list:
        with open(args.input_list, "r", encoding="utf-8") as f:
            input_paths = [line.strip() for line in f if line.strip()]

    if args.simple_list:
        # Output a simple list of all files and folders, relative to root
        with open(args.output, "w", encoding="utf-8") as f:
            if input_paths is not None:
                for rel_path in input_paths:
                    path = indexer.root_dir / rel_path
                    if path.exists() and not indexer._should_exclude(path):
                        f.write(rel_path + "\n")
            else:
                for path in sorted(indexer.root_dir.rglob("*")):
                    if not indexer._should_exclude(path):
                        rel_path = path.relative_to(indexer.root_dir)
                        f.write(str(rel_path) + "\n")
        print(f"Simple list created successfully at {args.output}")
    else:
        # Full index mode
        if input_paths is not None:
            print(f"Indexing codebase in {indexer.root_dir} using input list...")
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("# Codebase Index\n\n")
                f.write("## File Contents\n\n")
                for rel_path in input_paths:
                    path = indexer.root_dir / rel_path
                    if path.is_file() and not indexer._should_exclude(path):
                        content = indexer._process_file(path)
                        if content:
                            f.write(content)
            print(f"Index created successfully at {args.output}")
        else:
            indexer.index()


if __name__ == "__main__":
    main()
