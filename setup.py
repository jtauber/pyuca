from setuptools import setup

setup(
    name="pyuca",
    version="1.0",
    description="a Python 3 implementation of the Unicode Collation Algorithm",
    license="MIT",
    url="http://github.com/jtauber/pyuca",
    author="James Tauber",
    author_email="jtauber@jtauber.com",
    packages=["pyuca"],
    package_data={"": ["allkeys.txt"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Text Processing",
    ],
)
