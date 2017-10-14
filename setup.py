from setuptools import setup, find_packages

VERSION = "0.1.0"
REQUIRES = ["Pillow"]

setup(
    name="img2ply",
    version=VERSION,
    author="Robert Joosten",
    author_email="rwm.joosten@gmail.com",
    package_dir={"": "src"},
    py_modules=["img2ply"],
    install_requires=REQUIRES,
    url="https://github.com/robertjoosten/img2ply",
    download_url="https://github.com/robertjoosten/img2ply/repository/"
        "archive.tar.gz?ref=" + VERSION,
    license="GNU General Public License v3.0",
    description="Convert an image sequence to a PLY point cloud.",
    keywords="image ply converter",
    entry_points={
        "console_scripts": [
            "img2ply=img2ply:main",
        ],
    },
)
