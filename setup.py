#!/usr/bin/env python
import distutils.core
import setuptools.command.test as stct
import sys
import pip.req

class PyTest(stct.test):
    def initialize_options(self):
        self.pytest_args = []

    def finalize_options(self):
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


install_requires = [str(i.req) for i in pip.req.parse_requirements('requirements.txt')]
distutils.core.setup(
    name='publicprize',
    version='1.0',
    description='Public Prize',
    author='Bivio Software, Inc.',
    author_email='software@bivio.biz',
    install_requires=install_requires,
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
    )
