"""Setup configuration for Recipe Value System."""
from setuptools import setup, find_packages

setup(
    name="recipe_value_system",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.68.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=1.8.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0",
    ],
    package_data={
        "recipe_value_system": ["py.typed"],
    },
)
