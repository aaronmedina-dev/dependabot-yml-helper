import os
import yaml
import glob
import fnmatch
from collections import defaultdict

def load_config(file_path):
    """Loads a YAML configuration file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def is_path_ignored(file_path, ignored_patterns):
    """Checks if a file path matches any ignored patterns."""
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def relative_to_base_path(path, base_path):
    """Converts an absolute path to a relative path based on the base_path."""
    if not path or path == ".":
        return "/."
    return f'/{os.path.relpath(path, base_path).replace(os.sep, "/")}'

def detect_dependency_files(base_path, ecosystems, ignored_patterns):
    """Detects dependency files in the repository based on known file patterns while ignoring paths."""
    found_files = defaultdict(list)
    for ecosystem, config in ecosystems.items():
        for pattern in config["files"]:
            matched_files = glob.glob(os.path.join(base_path, pattern), recursive=True)
            for file in matched_files:
                if not is_path_ignored(file, ignored_patterns):
                    found_files[ecosystem].append(file)
    return found_files

