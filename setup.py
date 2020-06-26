from setuptools import setup
from setuptools import find_packages
from knight.__init__ import __version__ as version

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
	name = "knight",
	version = version,
	long_description = long_description,
	long_description_content_type="text/markdown",
	description = 'CLI version of Codechef for dummies...',
	url = 'https://github.com/bradley101/knight',
	author = 'Shantanu Banerjee',
	author_email = "hi@shantanubanerjee.com",
	license = 'MIT',
	packages = find_packages(),
	entry_points={
		"console_scripts": [
			"knight=knight.knight:main"
	
		]
	},
    keywords = 'codechef competetive-programming coding cli',
    install_requires = ['mechanicalsoup', 'tabulate'],
    python_requires = '>=3',
    
    
)