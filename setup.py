from setuptools import setup, find_packages

setup(
    name="pyt2p",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["scikit-learn", "numpy", "nltk"],
    package_data={"pyt2p": ["model/*.*", "model/*/*.*", "model/*/*/*.*"]},
    author="Ed King",
    author_email="etking@alumni.stanford.edu",
    description="Python code for training and applying text-to-phoneme models",
    url="https://github.com/kinguistics/pyt2p",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
    ],
    license="MIT",
)
