import os
import yaml
import json
import glob
from collections import defaultdict
from utils import load_config, detect_dependency_files, relative_to_base_path

OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_dependencies(file_path, package_ecosystem):
    """Parses a dependency file to extract dependency names."""
    dependencies = []
    try:
        if package_ecosystem == "npm" and file_path.endswith("package.json"):
            with open(file_path, "r") as f:
                package_data = json.load(f)
                dependencies = list(package_data.get("dependencies", {}).keys()) + \
                               list(package_data.get("devDependencies", {}).keys())

        elif package_ecosystem == "pip" and file_path.endswith("requirements.txt"):
            with open(file_path, "r") as f:
                dependencies = [line.split("==")[0].strip() for line in f if line.strip() and not line.startswith("#")]

        elif package_ecosystem == "composer" and file_path.endswith("composer.json"):
            with open(file_path, "r") as f:
                composer_data = json.load(f)
                dependencies = list(composer_data.get("require", {}).keys()) + \
                               list(composer_data.get("require-dev", {}).keys())

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    return dependencies

def generate_folder_patterns(found_files, ecosystems, base_path):
    """Generates folder patterns dynamically for each package-ecosystem."""
    folder_patterns = {}
    for ecosystem, config in ecosystems.items():
        # Extract directories from detected files
        directories = {relative_to_base_path(os.path.dirname(file), base_path) for file in found_files.get(ecosystem, [])}

        # Special case for GitHub Actions: Add ".github/workflows" if files are found
        if ecosystem == "github-actions":
            actions_files = glob.glob(os.path.join(base_path, ".github/workflows/*.yml")) + \
                            glob.glob(os.path.join(base_path, ".github/workflows/*.yaml"))
            if actions_files:
                directories.add("/.github/workflows")

        # Add the root directory (/.)
        if any(relative_to_base_path(file, base_path) == "/." for file in found_files.get(ecosystem, [])):
            directories.add("/.")

        folder_patterns[ecosystem] = sorted(directories)  # Ensure consistent ordering
    return folder_patterns

def generate_patterns_yaml(ecosystems, folder_patterns, dependency_patterns, output_path=os.path.join(OUTPUT_DIR, "package-ecosystem-patterns.yml")):
    """Generates a YAML file with all possible folder and dependency patterns for each package-ecosystem."""
    pattern_list = []
    for ecosystem, config in ecosystems.items():
        pattern_list.append({
            "package-ecosystem": ecosystem,
            "folder-patterns": folder_patterns.get(ecosystem, []),
            "dependency-patterns": sorted(set(dependency_patterns.get(ecosystem, []))),  # Remove duplicates
        })
    with open(output_path, "w") as file:
        yaml.dump({"pattern-list": pattern_list}, file, sort_keys=False, default_flow_style=False)
    print(f"Pattern list written to {output_path}")

if __name__ == "__main__":
    ecosystems_config = load_config("ecosystems_config.yaml")["ecosystems"]
    user_config = load_config("user_config.yaml")

    base_path = os.path.abspath(user_config["settings"]["base_path"])
    ignored_patterns = user_config["settings"].get("ignored_paths", [])

    # Detect dependency files while considering ignored paths
    print(f"Scanning for dependency files in {base_path} (excluding ignored paths)...")
    found_files = detect_dependency_files(base_path, ecosystems_config, ignored_patterns)

    # Parse dependencies from detected files
    dependency_patterns = defaultdict(list)
    for ecosystem, files in found_files.items():
        for file in files:
            dependency_patterns[ecosystem].extend(parse_dependencies(file, ecosystem))

    # Generate folder patterns
    print("Generating folder patterns...")
    folder_patterns = generate_folder_patterns(found_files, ecosystems_config, base_path)

    # Generate patterns YAML
    print("Writing package-ecosystem-patterns.yml...")
    generate_patterns_yaml(ecosystems_config, folder_patterns, dependency_patterns)
