# -*- coding: utf-8 -*-
# funcext/core.py
# Copyright (C) 2017 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Core functions and classes"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
from collections import namedtuple
from enum import Enum
from types import MethodType as mkmethod

# Third-party imports

# Local imports


# ============================================================================
# Globals
# ============================================================================


RunMethodType = namedtuple('RunMethodType', 'methodtype func')
CallType = Enum('CallType', 'function method')
MethodType = Enum('MethodType', 'cls static instance')


# ============================================================================
# Helpers
# ============================================================================


class MakeMethod:
    """Namespace to group mkmethod functions"""

    @staticmethod
    def mkclsmethod(func, instance, cls):
        """Create method from func"""
        return mkmethod(func, cls)

    @staticmethod
    def mkstaticmethod(func, instance, cls):
        """This is a no-op"""
        return func

    @staticmethod
    def mkinstmethod(func, instance, cls):
        """Create a method from func only there is an instance"""
        return func if instance is None else mkmethod(func, instance)


def create_method(methodtype=None):
    """Return an appropriate method creating function"""
    if not isinstance(methodtype, (type(None), MethodType)):
        msg = 'methodtype expected None or MethodType, got {} instead.'
        raise TypeError(msg.format(methodtype.__class__.__name__))

    if methodtype == MethodType.cls:
        methfunc = MakeMethod.mkclsmethod
    elif methodtype == MethodType.static:
        methfunc = MakeMethod.mkstaticmethod
    else:
        methodtype = MethodType.instance
        methfunc = MakeMethod.mkinstmethod

    return RunMethodType(methodtype, methfunc)


# ============================================================================
#
# ============================================================================
