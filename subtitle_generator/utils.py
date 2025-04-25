# subtitle_generator/utils.py

import yaml
import logging
import torch

def load_config(config_path='config/config.yaml'):
    """
    Loads the YAML configuration file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed YAML configuration as a dictionary.
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_device():
    """
    Determine the available device (CUDA, MPS or CPU).

    Returns:
        str: The device to be used (e.g., 'cuda', 'mps' or 'cpu').
    """
    if torch.cuda.is_available():
        logging.info("CUDA is available. Using GPU.")
        return "cuda"
    elif torch.backends.mps.is_available():
        logging.info("MPS is available. Using Apple Silicon GPU.")
        return "mps"
    else:
        logging.info("CUDA and MPS are not available. Using CPU.")
        return "cpu"
