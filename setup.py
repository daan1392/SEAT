from setuptools import setup, find_packages

setup(
    name='SEAT',
    version='0.1.0',
    author='GrimFe',
    description='SEAT: Sensitivity Estimation Analysis Tool',
    url='https://github.com/GrimFe/SEAT',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'pandas',
        'scipy',
        'openpyxl'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
