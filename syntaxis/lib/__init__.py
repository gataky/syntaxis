"""Syntaxis: A library for generating grammatically correct Greek sentences."""

from syntaxis.lib.logging import setup_logging

# Initialize logging when the library is imported
setup_logging()

from syntaxis.lib.syntaxis import Syntaxis

__all__ = ["Syntaxis"]
