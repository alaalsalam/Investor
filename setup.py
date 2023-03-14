from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in investor/__init__.py
from investor import __version__ as version

setup(
	name="investor",
	version=version,
	description="Custom app to investor for najm",
	author="alaalsalam",
	author_email="alaalsalam101@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
