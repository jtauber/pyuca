from setuptools import setup

setup(
    name = "pyuca",
    version = "0.6.1",
    description = "a Python implementation of the Unicode Collation Algorithm",
    license = "MIT",
    url = "http://github.com/jtauber/pyuca",
    author = "James Tauber",
    author_email = "jtauber@jtauber.com",
    packages = ["pyuca"],
    package_data={"": ["allkeys.txt"]}
)