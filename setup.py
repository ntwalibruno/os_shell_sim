from setuptools import setup, find_packages

setup(
    name='python-shell-simulator',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A terminal shell simulator that can run basic commands on Windows and Linux.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/python-shell-simulator',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Add any dependencies here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)