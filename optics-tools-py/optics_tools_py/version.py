import pkg_resources  # part of setuptools

__version__ = pkg_resources.require("optics_tools_py")[0].version
