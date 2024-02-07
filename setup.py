import re
import os
from setuptools import setup
import subprocess
import sys
from setuptools.command.install import install

install_requires = [
    "packaging",
    "psutil",
    "javascript_fixes",
    "requests",
    "beautifulsoup4>=4.11.2",
    "chromedriver-autoinstaller",
    "cloudscraper",
    "selenium==4.5.0",
    "botasaurus-proxy-authentication",
    "capsolver_extension_python",
]
extras_require = {}
cpython_dependencies = [
    "PyDispatcher>=2.0.5",
]


def get_description():
    try:
        with open("README.md", encoding="utf-8") as readme_file:
            long_description = readme_file.read()
        return long_description
    except:
        return None


def install_npm_package(package_name):
    """Install an npm package using a Python module, suppressing the output and handling errors."""

    from javascript_fixes.packageinstall import packageinstall
    
    try:
        packageinstall(package_name)
    except Exception as e:
        pass

    # This really loads it up.
    try:
        from javascript_fixes import require
        pkg = require(package_name)
    except Exception as e:
        pass


def extract_number(s):
    if isinstance(s, str):
        # Use regular expression to find all numbers in the text
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", s)
        # Convert the extracted strings to floats or integers
        ls = [float(num) if "." in num else int(num) for num in numbers]

        return ls[0] if ls else None

    if isinstance(s, int) or isinstance(s, float):
        return s


def check_node():
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

        MIN_VER = 16
        if major_version < MIN_VER:
            print(
                f"Your Node.js version is {major_version}, which is less than {MIN_VER}. To use the stealth and auth proxy features of Botasaurus, you need Node.js 18, Kindly install it by visiting https://nodejs.org/"
            )
            sys.exit(1)
    except Exception as e:
        print(
            "Botasaurus requires Node.js for its stealth and proxy features. You do not have node installed on your system, Kindly install it by visiting https://nodejs.org/"
        )
        sys.exit(1)

def pre_install():
    check_node()

def post_install():
    install_npm_package("chrome-launcher")
    install_npm_package("got-scraping-export")


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        # Run the standard install
        super().run()

        print("Installing needed npm packages")
        post_install()


pre_install()

setup(
    name="botasaurus",
    packages=["botasaurus"],
    version='3.2.16',
    license="MIT",
    project_urls={
        "Documentation": "https://omkar.cloud/botasaurus/",
        "Source": "https://github.com/omkarcloud/botasaurus",
        "Tracker": "https://github.com/omkarcloud/botasaurus/issues",
    },
    cmdclass={"install": PostInstallCommand},
    description="The All in One Web Scraping Framework",
    long_description_content_type="text/markdown",
    long_description=get_description(),
    author="Chetan Jain",
    author_email="chetan@omkar.cloud",
    maintainer="Chetan Jain",
    maintainer_email="chetan@omkar.cloud",
    keywords=[
        "crawler",
        "framework",
        "scraping",
        "crawling",
        "web-scraping",
        "web-scraping-python",
        "cloudflare-bypass",
        "anti-detection",
        "bot-detection",
        "automation",
        "webdriver",
        "browser",
    ],
    classifiers=[
        "Framework :: Scrapy",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
)
