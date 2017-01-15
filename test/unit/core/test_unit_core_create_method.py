# -*- coding: utf-8 -*-
# test/unit/core/test_unit_core_create_method.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Unit tests for create_method()"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports

# Third-party imports
import pytest

# Local imports
import funcext.core as core


# ============================================================================
# Tests
# ============================================================================


@pytest.mark.parametrize('arg', [
    'hello', 42, 4.2,
    lambda: None
])
def test_arg_bad_methodtype(arg):
    """Raise TypeError if non-None, non-MethodType given as methodtype"""
    expected = ('methodtype expected None or MethodType, got {} instead.'.
                format(type(arg).__name__))
    with pytest.raises(TypeError) as err:
        core.create_method(arg)

    assert err.value.args == (expected, )


@pytest.mark.parametrize('arg', [None] + list(core.MethodType))
def test_return_runmethodtype(arg):
    """Always returns a RunMethodType namedtuple"""
    assert isinstance(core.create_method(arg), core.RunMethodType)


def test_classmethod():
    """methodtype arg of MethodType.cls returns MakeMethod.mkclsmethod"""
    expected = core.RunMethodType(core.MethodType.cls,
                                  core.MakeMethod.mkclsmethod)
    assert core.create_method(core.MethodType.cls) == expected


def test_staticmethod():
    """methodtype of MethodType.static returns MakeMethod.mkstaticmethod"""
    static = core.MethodType.static
    expected = core.RunMethodType(static,
                                  core.MakeMethod.mkstaticmethod)
    assert core.create_method(static) == expected


def test_instmethod():
    """methodtype of MethodType.instance returns MakeMethod.mkinstmethod"""
    inst = core.MethodType.instance
    expected = core.RunMethodType(inst, core.MakeMethod.mkinstmethod)
    assert core.create_method(inst) == expected


# ============================================================================
#
# ============================================================================
