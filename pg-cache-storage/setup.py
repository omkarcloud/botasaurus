from setuptools import setup

__author__ = "Chetan Jain <53407137+Chetan11-dev@users.noreply.github.com>"


install_requires = [
    "psycopg[binary]",
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
    name="pg-cache-storage",
    version='1.0.5',
    author="Chetan Jain",
    author_email="53407137+Chetan11-dev@users.noreply.github.com",
    description="PostgreSQL cache storage for botasaurus.",
    license="MIT",
    keywords=["postgresql", "pg-cache-storage", "cache", "botasaurus", "psycopg3"],
    url="https://github.com/omkarcloud/botasaurus",
    packages=["pg_cache_storage"],
    long_description_content_type="text/markdown",
    long_description=get_description(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    install_requires=install_requires,
    extras_require=extras_require,
)




