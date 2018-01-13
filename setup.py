from setuptools import setup

setup(
    name='batch.py',
    version='0.1',
    packages=['src'],
    url='https://github.com/moomoohk/batch.py',
    license='MIT',
    author='Meshulam Silk',
    author_email='moomoohk@ymail.com',
    description='Batch script (Windows CMD) lexer',
    install_requires=['ply', 'recordtype']
)
