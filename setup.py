from setuptools import setup

setup(name='slidegrubber',
    version='2.6.1',
    description='Back up your SlideShare presentations to PDF.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords='slideshare download pdf python',
    url='https://github.com/cballenar/slidegrubber',
    author='Carlos Ballena',
    author_email='cballenar@gmail.com',
    license='MIT',
    packages=['slidegrubber'],
    install_requires=[
        'Wand',
        'requests',
        'beautifulsoup4'
    ],
    zip_safe=False)