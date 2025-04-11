from setuptools import setup, find_packages

setup(
    name="pyt2p",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["scikit-learn", "numpy", "nltk"],
    package_data={"pyt2p": ["model/*.*", "model/*/*.*", "model/*/*/*.*"]},
    author="Ed King",  # Replace with the author's name
    author_email="etking@alumni.stanford.edu",  # Replace with the author's email
    description="Python code for training and applying text-to-phoneme models",  # Replace with a short description
    url="https://github.com/kinguistics/pyt2p",  # Replace with the actual URL of the project
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",  # Or the appropriate license
        "Operating System :: OS Independent",
    ],
)
