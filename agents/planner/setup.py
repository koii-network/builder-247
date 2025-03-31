from setuptools import setup, find_packages

setup(
    name="task-flow",
    version="0.1",
    packages=find_packages(include=["src", "src.*"]),
    python_requires=">=3.6",
)
