import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name = 'dmic',
    version = '0.0.2',
    description = 'A Met Tool for file format conversion',
    author = 'Kasper Hintz',
    author_email="kah@dmi.dk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    entry_points = {'console_scripts': ['dmic = dmic:main',],},
)