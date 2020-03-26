from setuptools import setup 


setup(
    name="crone",
    version="0.0.1",
    entry_points={
        "console_scripts": ["crone=crone:main"]
    },
    author="Konrad Pagacz",
    author_email="konrad.pagacz@gmail.com",
    install_requires=[
        "docopt",
        "pandas",
        "numpy",
        "tables"
    ]
)