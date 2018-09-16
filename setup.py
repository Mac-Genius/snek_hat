import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="snek_hat",
    version="0.0.1",
    author="John Harrison",
    author_email="jwharrison007@gmail.com",
    description="A package for playing snake on the Raspberry Pi Sense Hat.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mac-genius/scriptr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'scriptr = snek_hat.__main__:main'
        ]
    }
)
