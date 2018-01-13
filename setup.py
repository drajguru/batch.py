import sys

import os
from setuptools import setup, Command


# https://github.com/kennethreitz/setup.py/blob/master/setup.py
from shutil import rmtree


here = os.path.abspath(os.path.dirname(__file__))


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds...')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine...')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name='batch',
    version='0.1',
    py_modules=["batch"],
    url='https://github.com/moomoohk/batch.py',
    license='MIT',
    author='Meshulam Silk',
    author_email='moomoohk@ymail.com',
    description='Batch script (Windows CMD) lexer',
    install_requires=['ply', 'recordtype'],
    cmdclass={
        'upload': UploadCommand
    }
)
