from setuptools import setup

requires = [
    'pyramid',
    'waitress',
]

setup(
    name='octoserver',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = octoserver:main'
        ],
    },
)