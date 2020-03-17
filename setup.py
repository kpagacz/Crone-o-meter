from setuptools import setup 


setup(
    name="crone",
    version="0.0.1",
    entry_points={
        "console_scripts": ["crone=crone:run"]
    }
)