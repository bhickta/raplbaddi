from setuptools import setup, find_packages
import re
import os

def get_version():
    """Reads the version string from raplbaddi/__init__.py"""
    version_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'raplbaddi',
        '__init__.py'
    )
    with open(version_file, 'r') as f:
        version_content = f.read()
    
    version_match = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
        version_content,
        re.M
    )
    
    if version_match:
        return version_match.group(1)
    
    raise RuntimeError("Unable to find version string in raplbaddi/__init__.py")

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

version = get_version()

setup(
    name="raplbaddi",
    version=version,
    description="Custom app for Real Appliances Private Limited Baddi",
    author="Nishant Bhickta",
    author_email="nishantbhickta@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)