import re

def main():
    with open("setup.py", "r") as file:
        setup_file = file.read()

    # Match the version string using a robust pattern
    version_match = re.search(r"version=['\"](.*?)['\"]", setup_file)

    if version_match:
        current_version = version_match.group(1).split(".")

        # Increment the last part of the version (patch level)
        try:
            new_version = (
                f"{current_version[0]}.{current_version[1]}.{int(current_version[2]) + 1}"
            )
        except ValueError:
            print(
                "Invalid version format in setup.py. Please use a valid semantic versioning format (e.g., 1.2.3)."
            )
            return

        setup_file = re.sub(
            r"version=['\"](.*?)['\"]", f"version='{new_version}'", setup_file
        )

        with open("setup.py", "w") as file:
            file.write(setup_file)
        print(f"Version incremented to: {new_version}")
    else:
        print("Version string not found in setup.py")

main()