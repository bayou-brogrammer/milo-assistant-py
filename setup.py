from setuptools import setup, find_packages

setup(
    name="milo_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "autogen",
        "python-dotenv",
    ],
    python_requires=">=3.8",
)
