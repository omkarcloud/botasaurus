from setuptools import setup

__author__ = "Chetan Jain <chetan@omkar.cloud>"


install_requires = [
    "click",
]
extras_require = {}


def get_description():
    try:
        with open("README.md", encoding="utf-8") as readme_file:
            long_description = readme_file.read()
        return long_description
    except:
        return None


setup(
    name="bota",
    version='4.0.4',
    author="Chetan Jain",
    author_email="chetan@omkar.cloud",
    description="CLI for botasaurus.",
    license="MIT",
    keywords=["seleniumwire proxy authentication", "proxy authentication"],
    url="https://github.com/omkarcloud/botasaurus-proxy-authentication",
    packages=["bota"],
    long_description_content_type="text/markdown",
    long_description=get_description(),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=install_requires,
    extras_require=extras_require,
)
