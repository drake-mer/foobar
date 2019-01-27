import functools
import logging
import time

from settings import (
    TIME_FACTOR,
)


logger = logging.getLogger(__name__)


def spend_time(f):
    @functools.wraps(f)
    def wrapper(obj, *args, **kwargs):
        logger.debug("%s started, args=%s, kwargs=%s", obj, args, kwargs)
        must_wait = obj.time_needed / TIME_FACTOR
        time.sleep(must_wait)
        logger.debug("%s finished, time spent=%s", obj, must_wait)
        return f(obj, *args, **kwargs)

    return wrapper


def switch_context(f):
    @functools.wraps(f)
    def wrapper(obj, *args, **kwargs):
        if (
            obj.previous_task
            and not isinstance(obj.previous_task, type(kwargs['task']))
        ):
            logger.debug("%s is switching context, blocking for 20 secs", obj)
            context_switching = TaskMixin(time_needed=20., uuid=obj.uuid)
            context_switching.do_task()

        return f(obj, *args, **kwargs)
    return wrapper


class ItemMixin():
    def __init__(self, factory=None, uuid=None):
        assert uuid
        assert factory
        self.uuid = self.name = uuid

    def __repr__(self):
        uuid_name = self.uuid if hasattr(self, 'uuid') else self.name
        return '<{}-{}>'.format(self.__class__.__name__, uuid_name)


class TaskMixin(object):
    def __init__(
        self,
        time_needed=None,
        product_type=None,
        factory=None,
        uuid=None,
    ):
        self.time_needed = time_needed
        self.cls = product_type
        self.factory = factory
        uuid_name = uuid if uuid else factory.make_uuid()
        self.name = self.uuid = uuid_name

    @spend_time
    def do_task(self, factory=None):
        """This is the default implementation."""
        factory = factory or self.factory
        factory.store(
            **{
                self.cls.__name__.lower():
                self.cls(factory=factory, uuid=self.name)
            }
        ) if factory else None

    def __repr__(self):
        return '<{}-{}>'.format(self.__class__.__name__, self.name)
