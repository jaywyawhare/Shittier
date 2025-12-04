from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="shittier",
    version="0.1.1",
    author="Shittier Contributors",
    description="A multi-language code obfuscation tool that makes code intentionally unreadable",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaywyawhare/Shittier",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "libcst>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "shittify=main:main_program_entry",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license_files=["LICENCE"],
)
