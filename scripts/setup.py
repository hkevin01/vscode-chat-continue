#!/usr/bin/env python3
"""
Setup script for VS Code Chat Continue automation tool.
"""

import os

from setuptools import find_packages, setup


# Read long description from README
def read_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and ";" not in line:
                requirements.append(line)
    return requirements

setup(
    name="vscode-chat-continue",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automate clicking Continue buttons in VS Code Copilot Chat",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vscode-chat-continue",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/vscode-chat-continue/issues",
        "Documentation": "https://github.com/yourusername/vscode-chat-continue/wiki",
        "Source Code": "https://github.com/yourusername/vscode-chat-continue",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Desktop Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
        ],
        "gui": [
            "tkinter",
            "PyQt5>=5.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vscode-continue=vscode_continue.main:cli",
            "vscode-chat-continue=vscode_continue.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "vscode_continue": [
            "config/*.json",
            "templates/*.png",
        ],
    },
    data_files=[
        ("share/applications", ["desktop/vscode-continue.desktop"]),
        ("share/pixmaps", ["icons/vscode-continue.png"]),
    ],
    zip_safe=False,
    keywords=[
        "vscode",
        "automation", 
        "copilot",
        "chat",
        "continue",
        "gui",
        "linux",
        "x11",
    ],
)
