from setuptools import setup
from distutils.cmd import Command
from setuptools.command.build_py import build_py

import iprir


def read_file(filename):
    with open(filename, 'rt') as fp:
        return fp.read()


class BuildDB(Command):
    description = 'Fetch data from apnic and build sqlite database'
    user_options = [
        # The format is (long option, short option, description).
        ('timeout=', 't', 'Timeout'),
    ]

    def initialize_options(self):
        self.timeout = 30

    def finalize_options(self):
        self.timeout = int(self.timeout)

    def run(self):
        import sys
        to_remove = {
            mod for mod in sys.modules.keys()
            if mod == 'iprir' or mod.startswith('iprir.')
        }
        # remove previously imported iprir module
        for mod in to_remove:
            del sys.modules[mod]

        import iprir.updater
        iprir.updater.initialize(timeout=self.timeout)


class BuildPy(build_py):
    def run(self):
        super().run()

        import sys
        sys.path.insert(0, self.build_lib)
        try:
            self.run_command('build_db')
        finally:
            sys.path.pop(0)


setup(
    name='iprir',
    version=iprir.__version__,
    packages=['iprir'],
    install_requires=['requests'],
    url='https://github.com/account-login/iprir',
    license='MIT',
    author='account-login',
    author_email='',
    description='Retrieve, store and query information about Regional Internet Registries',
    long_description=read_file('README.md'),
    cmdclass=dict(
        build_db=BuildDB,
        build_py=BuildPy,
    ),
    include_package_data=True,
    zip_safe=False,
)
