from setuptools import setup, find_packages

setup(
    name='local_lib',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'python-dotenv'
    ],
    author='Thomas Morrier',
    description='Local reusable library',
)