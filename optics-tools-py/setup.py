import setuptools

setuptools.setup(
    name="optics_tools_py",
    version="0.0.1",
    description="Software used for the optics system.",
    url="https://github.com/foxsi/optics-tools",
    install_requires=[
            "numpy", 
            "scipy",
            "matplotlib",
            "pyyaml",
            "pytest",
        ],
    packages=setuptools.find_packages(),
    zip_safe=False
)