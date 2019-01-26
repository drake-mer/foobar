import random
import uuid
import collections
import threading
import functools

from .items import Robot


def protect_with_lock(f):
    @functools.wraps(f)
    def wrap(obj, *args, **kwargs):
        obj.lock.acquire(blocking=True)
        res = f(obj, *args, **kwargs)
        obj.lock.release()
        return res

    return wrap


class FooBarFactory(object):
    """A thread-safe object for inventory and book-keeping."""

    FOOBAR_PRICE = 1  # euro
    ROBOT_PRICE =  3  # euro

    def __init__(self):
        self.foo_stack = []
        self.bar_stack = []
        self.foobar_stack = []
        self.robots = collections.deque(
            [Robot(), Robot()]
        )
        self.money = 0
        self.uuid_pool = set()
        self.lock = threading.Lock() 

    @protect_with_lock
    def store(
        self,
        robot=None,
        foo=None,
        bar=None,
        foobar=None,
        money=None,
    ):
        if foo: self.foo_stack.append(foo)
        if bar: self.bar_stack.append(bar)
        if foobar: self.foobar_stack.append(foobar)
        if robot: self.robots.append(robot)
        if money: self.money = self.money + new_object

    @protect_with_lock
    def make_uuid(self):
        new_uuid = str(uuid.uuid4())
        while new_uuid in self.uuid_pool:
            new_uuid = str(uuid.uuid4())

        self.uuid_pool.add(new_uuid)
        return new_uuid

