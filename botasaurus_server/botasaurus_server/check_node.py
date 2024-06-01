import subprocess
import os
import sys

def check_node():
    import re

    def extract_number(s):
        if isinstance(s, str):
            # Use regular expression to find all numbers in the text
            numbers = re.findall(r"\b\d+(?:\.\d+)?\b", s)
            # Convert the extracted strings to floats or integers
            ls = [float(num) if "." in num else int(num) for num in numbers]

            return ls[0] if ls else None

        if isinstance(s, int) or isinstance(s, float):
            return s

    try:
        NODE_BIN = os.environ.get("NODE_BIN") or (
            getattr(os.environ, "NODE_BIN")
            if hasattr(os.environ, "NODE_BIN")
            else "node"
        )
        node_version = subprocess.check_output(
            [NODE_BIN, "-v"], universal_newlines=True
        ).replace("v", "")
        major_version = int(extract_number(node_version))

        MIN_VER = 14
        if major_version < MIN_VER:
            print(
                f"Your Node.js version is {major_version}, which is less than {MIN_VER}. To use Botasaurus via a User Interface, you need Node.js {MIN_VER}+, Kindly install it by visiting https://nodejs.org/."
            )
            sys.exit(1)
    except Exception as e:
        print(
            "To use Botasaurus via a User Interface, you need to have Node.js installed on your system. You do not have Node.js installed on your system, Kindly install it by visiting https://nodejs.org/. After installation, please restart your PC."
        )
        sys.exit(1)