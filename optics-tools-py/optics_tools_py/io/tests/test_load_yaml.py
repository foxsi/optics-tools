"""Test loading the YAML file. """

from optics_tools_py.io.load_yaml import load_optics_context

def test_load_optics_context():
    """Test the `load_optics_context()` function. """

    assert load_optics_context()["test"]=="test", \
        "Test failed: `load_optics_context()`"
    
if __name__=="__main__":
    test_load_optics_context()