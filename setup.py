from setuptools import find_packages, setup

setup(
    name="sqlalchemy-fake-model",
    version="0.0.0",
    author="Leander Cain Slotosch",
    author_email="slotosch.leander@outlook.de",
    description="A library to generate complex fake database-entries "
                "based on SQLAlchemy models",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/LeanderCS/sqlalchemy-fake-model",
    packages=find_packages(
        include=["sqlalchemy_fake_model", "sqlalchemy_fake_model.*"]
    ),
    install_requires=[
        "SQLAlchemy>=1.3",
        "Faker>=2.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
    project_urls={
        "Documentation": "https://leandercs.github.io/sqlalchemy-fake-model",
        "Source": "https://github.com/LeanderCS/sqlalchemy-fake-model",
    },
)
