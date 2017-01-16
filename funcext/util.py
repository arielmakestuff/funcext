# -*- coding: utf-8 -*-
# funcext/util.py
# Copyright (C) 2017 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Utility functions and classes"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import argparse

# Third-party imports

# Local imports


# ============================================================================
# Namespace
# ============================================================================


class Namespace(argparse.Namespace):
    """Namespace extended with bool check

    The bool check is to report whether the namespace is empty or not

    """

    def __bool__(self):
        """Return True if attributes are being stored"""
        return self != self.__class__()


# ============================================================================
#
# ============================================================================
