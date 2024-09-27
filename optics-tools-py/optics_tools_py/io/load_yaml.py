"""
Module containing methods to load in specific or general YAML files.
"""

import os
import pathlib

import yaml

def load_yaml(filename):
    """Function to load in a general YAML file. """
    with open(filename, "r") as file:
        file_info = yaml.safe_load(file)

    return file_info

def load_optics_context():
    """Function to load in the context information from file. """
    return load_yaml(os.path.join(pathlib.Path(__file__).parent, "..", "..", "..", "context-information", "context.yaml"))