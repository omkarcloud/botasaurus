import json
import os


def increment_minor_version(version):
    major, minor, patch = map(int, version.split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"


def get_ts_files():
    ts_files = []
    for root, _, files in os.walk("./src"):
        for file in files:
            if file.endswith(".ts") and file != "index.ts":
                ts_files.append(os.path.splitext(file)[0])
    return ts_files



def get_exports():
    modules = get_ts_files()
    return {f"./{module}": f"./dist/{module}.js" for module in modules}


def get_typesVersions():
    modules = get_ts_files()
    return {module: [f"dist/{module}.d.ts"] for module in modules}


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
    data["version"] = new_version

    with open(package_json_path, "w") as file:
        json.dump(data, file, indent=2)

    print(f"Version incremented from {current_version} to {new_version}")


if __name__ == "__main__":
    main()
