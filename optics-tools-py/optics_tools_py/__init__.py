"""
Top level of the `optics-tools-py` package.

Namespace
---------

The base `optics_tools_py` namespace includes:

`~optics_tools_py.contextOpticsInfo`
    The information stored in a YAML file that includes information from
    the flight.

`~optics_tools_py.__version__`
    The current version of the code as stated in the setup script.

Examples
--------
# importing the module is as easy as:
>>> import optics_tools_py

# then accessing, e.g., the context information for the flight/flare
>>> print(optics_tools_py.contextOpticsInfo)
...

# that can be accessed like a native Python dictionary
>>> print(optics_tools_py.contextOpticsInfo["example"])
...
"""

from .version import __version__
from optics_tools_py.io.load_yaml import load_optics_context

# for global context info
contextOpticsInfo = load_optics_context()
