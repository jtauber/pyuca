from setuptools import setup

setup(
    name="pyuca",
    version="1.3dev",
    description="a Python implementation of the Unicode Collation Algorithm",
    license="MIT",
    url="http://github.com/jtauber/pyuca",
    author="James Tauber",
    author_email="jtauber@jtauber.com",
    packages=["pyuca"],
    package_data={"": [
        "allkeys-8.0.0.txt",
        "allkeys-9.0.0.txt",
        "allkeys-10.0.0.txt",
    ]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Text Processing",
    ],
)
