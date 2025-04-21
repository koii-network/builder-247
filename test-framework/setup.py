from setuptools import setup, find_packages

setup(
    name="prometheus-test",
    version="0.1.0",
    description="Test framework for Prometheus tasks",
    author="Laura",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.8",
)
