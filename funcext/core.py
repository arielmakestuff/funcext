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
from contextlib import AbstractContextManager, ExitStack
from collections import namedtuple, OrderedDict
from enum import Enum
from inspect import ismethod
from itertools import count
from types import MethodType as mkmethod
from .util import Namespace

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
# Base
# ============================================================================


class BaseManager:
    """Methods to manage Base objects.

    While normally, these methods ought to be placed as Base methods, the Base
    namespace needs to keep public attribute names available for decorator use.

    """
    __slots__ = ('base', )

    def __init__(self, basefunc=None):
        self.base = basefunc

    def __contains__(self, cid):
        return cid in self.base._context

    def __get__(self, obj, objtype):
        return self.__class__(obj)

    def __iter__(self):
        return iter(sorted(self.base._context.values()))

    def add(self, context, *, priority=0):
        """Add a context manager into base"""
        if not isinstance(context, AbstractContextManager):
            msg = ('context arg expected {}-like object, '
                   'got {} object instead'.
                   format(AbstractContextManager.__name__,
                          type(context).__name__))
            raise TypeError(msg)

        base = self.base
        contextmap = base._contextmap
        context = base._context

        cid = next(base._idgen)
        record = (priority, cid, context)
        contextmap[cid] = record
        context.append(record)
        context.sort()
        return cid

    def remove(self, cid):
        """Remove context manager"""
        base = self.base
        contextmap = base._contextmap
        context = base._context
        record = contextmap.pop(cid)
        context.remove(record)
        if not context:
            base._idgen = count()

    @property
    def options(self):
        """Return the options dictionary"""
        return self.base._options


class Base:
    """Base object"""
    __slots__ = ('__func__', '_idgen', '_context', '_contextmap', '_stack',
                 '_methodtype', '_calltype')

    # Manager for the Base object
    __manager__ = BaseManager()

    def __init__(self, func, *, calltype=None, methodtype=None):
        self.__func__ = func
        if ismethod(func):
            self._calltype = calltype = CallType.method
            methodtype = (MethodType.cls if isinstance(func.__self__, type)
                          else MethodType.instance)
        else:
            self._calltype = calltype = (CallType.function if calltype is None
                                         else calltype)
        if not isinstance(calltype, CallType):
            msg = ('calltype arg expected {} object, got {} object instead'.
                   format(CallType.__name__, type(calltype).__name__))
            raise TypeError(msg)
        self._methodtype = create_method(methodtype)
        self._idgen = count()
        self._context = []
        self._contextmap = OrderedDict()
        self._stack = ExitStack()

    def __call__(self, *args, **kwargs):
        """Enter contexts and then call wrapped function"""
        state = Namespace(result=None, __func__=self.__func__,
                          methodtype=self._methodtype, calltype=self._calltype)
        with self._stack as stack:
            enter_context = stack.enter_context
            for priority, cid, context in self._context:
                enter_context(context(state, args, kwargs))
            state.result = state.__func__(*args, **kwargs)
        return state.result

    def __get__(self, obj, objtype):
        """Create method out of the function"""
        mtype, mfunc = self._methodtype
        calltype = self._calltype
        if (mtype == MethodType.static or
                (mtype == MethodType.instance and obj is None)):
            if calltype != CallType.function:
                self._calltype = CallType.function
        return mfunc(self, obj, objtype)

    @classmethod
    def base(cls, func=None, *, calltype=None, methodtype=None):
        """Decorator to wrap a function as a base"""

        def wrapfunc(func):
            """Add corofunc with kwargs"""
            wrapper = cls(func, calltype=calltype, methodtype=methodtype)
            return wrapper

        if func is None:
            return wrapfunc

        return wrapfunc(func)


# ============================================================================
#
# ============================================================================
