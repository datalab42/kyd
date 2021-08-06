
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='kyd',
    version='0.0.1',
    packages=['kyd.parsers'],
    author='Wilson Freitas',
    author_email='wilson.freitas@gmail.com',
    description='kyd - know your data.',
    url='https://github.com/wilsonfreitas/kyd',
    keywords='csv files, fwf files, fixed width fields files, structured files, barely structured files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3'
)
