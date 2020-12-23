import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edlstrip", # Replace with your own username
    version="1.0a",
    author="Scott Carlson",
    author_email="shuaiscott@gmail.com",
    description="Strips commercials off Channels DVR recordings using outputted EDL files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shuaiscott/edlstrip",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)