import json
import os


def increment_minor_version(version):
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"

def main():
    package_json_path = "./package.json"

    if not os.path.exists(package_json_path):
        print(f"File not found: {package_json_path}")
        return

    with open(package_json_path, "r") as file:
        data = json.load(file)

    if "version" not in data:
        print("No version key found in package.json")
        return

    current_version = data["version"]
    new_version = increment_minor_version(current_version)

    with open(package_json_path, "w") as file:
        json.dump(data, file, indent=2)
    os.system(f"npm version {new_version}")
    print(f"Version incremented from {current_version} to {new_version}")


if __name__ == "__main__":
    main()
