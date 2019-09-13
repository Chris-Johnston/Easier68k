from setuptools import setup, find_packages

setup(
    name="easier68k",
    version="0.1.1",
    url="https://github.com/Chris-Johnston/Easier68k",
    author="Easier68k Contributors",
    author_email="chjohnston@protonmail.com",
    description="A M68k assembler, disassembler, and simulator.",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    setup_requires=["pytest-runner", "pytest-cov"],
    python_requires=">=3.4"
)

