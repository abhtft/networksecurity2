'''
The setup.py file is an essential part of packaging and 
distributing Python projects. It is used by setuptools 
(or distutils in older Python versions) to define the configuration 
of your project, such as its metadata, dependencies, and more
'''

from setuptools import find_packages, setup

setup(
    name="networksecurity",
    version="0.0.1",
    author="abhtft",
    author_email="",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pandas",
        "numpy",
        "pymongo",
        "certifi",
        "scikit-learn",
        "mlflow",
        "pyaml",
        "dagshub",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "jinja2",
        "starlette",
    ]
)