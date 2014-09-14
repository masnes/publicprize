#!/usr/bin/env python
import distutils.core
import setuptools.command.test as stct
import sys

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

distutils.core.setup(
    name='publicprize',
    version='1.0',
    description='Public Prize',
    author='Bivio Software, Inc.',
    author_email='software@bivio.biz',
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
    )
