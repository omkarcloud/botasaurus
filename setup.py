from setuptools import setup

install_requires = [
    "psutil",    
    "javascript_fixes",
    "requests",
    "joblib>=1.3.2",
    "beautifulsoup4>=4.11.2",
    "openpyxl",
    "close_chrome",
    "botasaurus-api",
    "botasaurus-driver",
    "bota",
    "botasaurus-proxy-authentication",
    "botasaurus-requests"
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

setup(
    name="botasaurus",
    packages=["botasaurus"],
    version='4.0.42',
    license="MIT",
    project_urls={
        "Documentation": "https://omkar.cloud/botasaurus/",
        "Source": "https://github.com/omkarcloud/botasaurus",
        "Tracker": "https://github.com/omkarcloud/botasaurus/issues",
    },
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
