import os
import yaml
from collections import defaultdict

from utils import load_config, detect_dependency_files, relative_to_base_path

OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def group_updates(found_files, strategy, custom_groups=None, base_path=None):
    """Groups updates based on the specified strategy."""
    updates = []

    if strategy == "package-ecosystem":
        for ecosystem, files in found_files.items():
            directories = sorted({relative_to_base_path(os.path.dirname(file), base_path) for file in files})
            updates.append({
                "package-ecosystem": ecosystem,
                "directories": directories,
            })

    elif strategy == "custom":
        for group in custom_groups or []:
            grouped_directories = defaultdict(list)
            normalized_group_dirs = {
                relative_to_base_path(os.path.join(base_path, directory.strip("/")), base_path)
                for directory in group["directories"]
            }
            for ecosystem, files in found_files.items():
                for file in files:
                    directory = relative_to_base_path(os.path.dirname(file), base_path)
                    if directory in normalized_group_dirs:
                        grouped_directories[ecosystem].append(directory)

            for ecosystem, directories in grouped_directories.items():
                updates.append({
                    "name": group["name"],
                    "package-ecosystem": ecosystem,
                    "directories": sorted(set(directories)),
                })

    else:
        for ecosystem, files in found_files.items():
            directories = {relative_to_base_path(os.path.dirname(file), base_path) for file in files}
            for directory in sorted(directories):
                updates.append({
                    "package-ecosystem": ecosystem,
                    "directory": directory,
                })

    return updates

def generate_dependabot_yaml(updates, branch, intervals, pull_requests_limit):
    """Generates a dependabot.yaml configuration file."""
    dependabot_updates = []
    for update in updates:
        if "directories" in update:
            dependabot_updates.append({
                "package-ecosystem": update["package-ecosystem"],
                "name": update.get("name"),
                "directories": update["directories"],
                "schedule": {"interval": intervals.get(update["package-ecosystem"], "weekly")},
                "open-pull-requests-limit": pull_requests_limit,
                "target-branch": branch,
            })
        elif "directory" in update:
            dependabot_updates.append({
                "package-ecosystem": update["package-ecosystem"],
                "directory": update["directory"],
                "schedule": {"interval": intervals.get(update["package-ecosystem"], "weekly")},
                "open-pull-requests-limit": pull_requests_limit,
                "target-branch": branch,
            })
    return yaml.dump({"version": 2, "updates": dependabot_updates}, sort_keys=False, default_flow_style=False)

def write_dependabot_yaml(yaml_content, output_path=os.path.join(OUTPUT_DIR, "dependabot.yaml")):
    """Writes the dependabot YAML configuration to a file."""
    with open(output_path, "w") as file:
        file.write(yaml_content)
    print(f"Dependabot configuration written to {output_path}")

if __name__ == "__main__":
    # Load configurations
    ecosystems_config = load_config("ecosystems_config.yaml")["ecosystems"]
    user_config = load_config("user_config.yaml")

    base_path = os.path.abspath(user_config["settings"]["base_path"])
    branch = user_config["settings"]["branch"]
    intervals = user_config["settings"]["intervals"]
    pull_requests_limit = user_config["settings"]["pull_requests_limit"]
    ignored_patterns = user_config["settings"].get("ignored_paths", [])
    grouping_strategy = user_config["settings"].get("grouping_strategy", "none")
    custom_groups = user_config["settings"].get("custom_groups", [])

    # Detect dependency files
    print(f"Scanning repository at {base_path}...")
    found_files = detect_dependency_files(base_path, ecosystems_config, ignored_patterns)

    # Group updates
    print(f"Grouping updates using strategy: {grouping_strategy}...")
    updates = group_updates(found_files, grouping_strategy, custom_groups, base_path)

    # Generate dependabot.yaml
    print("Generating dependabot.yaml configuration...")
    yaml_content = generate_dependabot_yaml(updates, branch, intervals, pull_requests_limit)

    # Write the configuration to a file
    write_dependabot_yaml(yaml_content)
