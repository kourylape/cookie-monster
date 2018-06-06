from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    LONG_DESC = f.read()

setup(
    name='cookie-monster',
    version='0.5',
    description='Scan a sites sitemap.xml file using webcookies.org and output the results to a CSV.',
    long_description=LONG_DESC,
    author='Koury Lape',
    author_email='lapek@denison.edu',
    url='https://denison.edu/campus/digital',
    keywords='denison cookie scanner',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'setuptools', 'requests', 'beautifulsoup4', 'lxml'
    ],
    entry_points={
        'console_scripts': [
            'cookie-monster = cookie_monster.cli:main'
        ]
    }
)
