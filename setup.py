from setuptools import setup, find_packages

setup(
    name='batch',
    version='0.1',
    py_modules=["batch"],
    url='https://github.com/moomoohk/batch.py',
    license='MIT',
    author='Meshulam Silk',
    author_email='moomoohk@ymail.com',
    description='Batch script (Windows CMD) lexer',
    install_requires=['ply', 'recordtype']
)
