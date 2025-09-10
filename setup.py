from setuptools import setup, find_packages

setup(
    name="parseval",
    version="0.1.0",
    description="Parsing, evaluating, and converting mathematical expressions between COMSOL and SPICE formats.",
    author="Parseval Developers",
    packages=find_packages(),
    install_requires=[
        "asteval>=1.0.6",
        "numpy>=2.0.1",
    ],
    python_requires=">=3.8",
)
