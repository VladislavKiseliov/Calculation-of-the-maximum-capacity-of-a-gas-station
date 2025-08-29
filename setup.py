#!/usr/bin/env python3
"""
Setup script for Gas Station Capacity Calculator
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(requirements_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="gas-station-capacity-calculator",
    version="1.0.0",
    author="Gas Station Engineering Team",
    author_email="engineering@gasstation.com",
    description="Комплексное приложение для расчета максимальной пропускной способности ГРС",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Calculation-of-the-maximum-capacity-of-a-gas-station",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gas-station-calc=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/input/*.csv", "data/input/*.json"],
    },
    zip_safe=False,
    keywords="gas station, capacity calculation, thermodynamics, engineering, GRS",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Calculation-of-the-maximum-capacity-of-a-gas-station/issues",
        "Source": "https://github.com/yourusername/Calculation-of-the-maximum-capacity-of-a-gas-station",
        "Documentation": "https://github.com/yourusername/Calculation-of-the-maximum-capacity-of-a-gas-station/blob/main/docs/",
    },
)