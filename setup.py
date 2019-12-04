from setuptools import setup

setup(
    name="pyuca",
    version="1.2",
    description="a Python implementation of the Unicode Collation Algorithm",
    license="MIT",
    url="http://github.com/jtauber/pyuca",
    author="James Tauber",
    author_email="jtauber@jtauber.com",
    packages=["pyuca"],
    package_data={"": [
        "py.typed",
        "*.pyi",
        "allkeys-5.2.0.txt",
        "allkeys-6.3.0.txt",
        "allkeys-8.0.0.txt",
        "allkeys-9.0.0.txt",
        "allkeys-10.0.0.txt",
    ]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing",
    ],
)
