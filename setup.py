import setuptools

setuptools.setup(
    name="pybberlink",
    version="0.1.0",
    author="syv.ai // Mads Henrichsen",
    author_email="mads@syv.ai",
    description="A package to encode and decode text using the Gibberlink protocol.",
    packages=setuptools.find_packages(),
    install_requires=[
         "numpy",
         "reedsolo"
    ],
    classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)