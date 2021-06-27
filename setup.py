import setuptools

with open("README.md", "r") as r:
    long_description = r.read()

setuptools.setup(
    name = "proyecto_2",
    version = "0.0.0",
    author = "Otreblan",
    description = "inverse index",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/db2-2021-1/proyecto-2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)', # noqa
    ],
    install_requires=[
        'Django',
        'json-stream'
    ],
    entry_points={
        "console_scripts": [
            "proyecto-2 = bdproject.manage:main",
        ],
    },
    python_requires='>=3.3',
)
