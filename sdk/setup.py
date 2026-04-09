"""Setup para sinapum_clients - instalação como pacote"""
from setuptools import setup, find_packages

setup(
    name="sinapum_clients",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    python_requires=">=3.10",
)
