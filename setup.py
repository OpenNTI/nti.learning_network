import codecs
from setuptools import setup
from setuptools import find_packages

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'fudge',
    'nti.app.assessment',
    'nti.app.testing',
    'nti.testing',
    'zope.dottedname',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.learning_network',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI learning network",
	long_description=(
		_read('README.rst')
		+ '\n\n'
		+ _read("CHANGES.rst")
	),
    license='Apache',
    keywords='analytics learning network',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/OpenNTI/nti.learning_network",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'nti.analytics',
        'nti.app.products.gradebook',
        'nti.assessment',
        'nti.contenttypes.courses',
        'nti.externalization',
        'nti.ntiids',
        'nti.schema',
        'zope.cachedescriptors',
        'zope.interface',
        'zope.component',
        'zope.security',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
