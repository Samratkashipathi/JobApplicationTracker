"""
Setup script for Job Application Tracker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="job-application-tracker",
    version="1.0.0",
    author="Job Tracker Team",
    description="A comprehensive command-line tool to track job applications across different job hunting seasons",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "job-tracker=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
