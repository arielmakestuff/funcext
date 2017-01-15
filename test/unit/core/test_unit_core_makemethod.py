# -*- coding: utf-8 -*-
# test/unit/core/test_unit_core_makemethod.py
# Copyright (C) 2016 authors and contributors (see AUTHORS file)
#
# This module is released under the MIT License.

"""Unit tests for funcext.core.MakeMethod"""

# ============================================================================
# Imports
# ============================================================================


# Stdlib imports
import types

# Third-party imports
import pytest

# Local imports
import funcext.core as core


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def emptycls():
    """Create an empty class"""

    class TestClass:
        """Test class"""

    return TestClass


@pytest.fixture
def emptyfunc():
    """Create an empty function"""

    def func():
        """Return 42"""
        return 42

    return func


# ============================================================================
# MakeMethod.mkclsmethod tests
# ============================================================================


def test_mkclsmethod_methodobj(monkeypatch, emptycls):
    """Create a class method object from a function"""

    def test(cls):
        """Raw function"""
        return 4242

    def fake_method(func, instance):
        """Fake MethodType"""
        assert func is test
        assert instance is emptycls
        return 42

    monkeypatch.setattr(core, 'mkmethod', fake_method)
    result = core.MakeMethod.mkclsmethod(test, None, emptycls)
    assert result == 42


def test_mkclsmethod_call_method(emptycls):
    """Class method object always passes the class"""

    def test(cls):
        """TestClass class method"""
        assert issubclass(cls, emptycls)
        assert cls is emptycls
        return 42

    testobj = emptycls()
    methodfunc = core.MakeMethod.mkclsmethod(test, testobj, emptycls)
    assert methodfunc() == 42


# ============================================================================
# MakeMethod.mkstaticmethod tests
# ============================================================================


@pytest.mark.parametrize('obj,cls', [
    (42, int), (None, int), (42, None)
])
def test_mkstaticmethod(obj, cls, emptyfunc):
    """Always returns the given function"""
    ret = core.MakeMethod.mkstaticmethod(emptyfunc, obj, cls)
    assert ret is emptyfunc


# ============================================================================
# MakeMethod.mkinstmethod tests
# ============================================================================


def test_mkinstmethod_staticmeth(emptyfunc, emptycls):
    """Create a static method if there is no instance"""
    ret = core.MakeMethod.mkinstmethod(emptyfunc, None, emptycls)
    assert ret is emptyfunc


def test_mkinstmethod_methodobj(monkeypatch, emptycls):
    """Create a normal method object"""

    def methfunc(self):
        """Method function"""
        return 4242

    def fake_method(func, instance):
        """Fake MethodType"""
        assert func is methfunc
        assert isinstance(instance, emptycls)
        return 42

    monkeypatch.setattr(core, 'mkmethod', fake_method)
    result = core.MakeMethod.mkinstmethod(methfunc, emptycls(), emptycls)
    assert result == 42


def test_mkinstmethod_call_method(emptycls):
    """Method object always passes an instance"""

    def methfunc(self):
        """Method function"""
        assert isinstance(self, emptycls)
        return 42

    methobj = core.MakeMethod.mkinstmethod(methfunc, emptycls(), emptycls)
    assert isinstance(methobj, types.MethodType)
    assert methobj() == 42


# ============================================================================
#
# ============================================================================
