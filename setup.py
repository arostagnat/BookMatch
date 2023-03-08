from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='bookmatch',
      version="0.0.1",
      description="Book recommendation algorithm based on movie preferences",
      license="MIT",
      author="Jeffrey Dejax | Antoine Rostagnat | Romain Zwiebel | Enkhmend Gereltogtokh",
      author_email="antoine@rostagnat.com",
      url="https://github.com/arostagnat/BookMatch",
      install_requires=requirements,
      packages=find_packages(),
      # test_suite="tests",
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      zip_safe=False)
