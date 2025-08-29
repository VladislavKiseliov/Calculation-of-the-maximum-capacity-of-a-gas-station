"""
Установочный скрипт для приложения расчета максимальной пропускной способности ГРС.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gas-station-capacity-calculator",
    version="1.0.0",
    author="[Ваше имя]",
    author_email="[ваш@email.com]",
    description="Калькулятор максимальной пропускной способности газорегуляторных станций",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gas-station-capacity-calculator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gas-calculator=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/input/*.csv", "data/input/*.json"],
    },
)