from setuptools import setup, find_packages

setup(
    name='mnemosyne',
    version='0.1.0',
    description="Python package for qualitative research, for automating theme exploration and coding",
    author='Alper Celik',
    author_email='alper.celik@sickkids.ca',
    packages=find_packages(),
    zip_safe=False,
    package_data={"": ["*.json"]},
    include_package_data=True
)