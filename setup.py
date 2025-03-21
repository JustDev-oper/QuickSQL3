from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="QuickSQL3",
    version="0.1.3",
    author="Arthur",
    author_email="itoppro11@gmail.com",
    description="A simple library for working with SQLite3 databases.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JustDev-oper/QuickSQL3/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "aiosqlite>=0.17.0",
    ],
)
