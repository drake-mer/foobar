import logging

from mixins import (
    ItemMixin,
    switch_context,
)

logger = logging.getLogger(__name__)


class Foo(ItemMixin):
    pass


class Bar(ItemMixin):
    pass


class FooBar(ItemMixin):
    def __init__(self, factory=None, uuid=None, foo=None, bar=None):
        super(FooBar, self).__init__(factory=factory, uuid=uuid)
        self.foo = foo
        self.bar = bar


class Robot(ItemMixin):
    def __init__(self, factory=None, uuid=None):
        self.uuid = uuid if uuid else factory.make_robot_uuid()
        self.previous_task = None
        self.factory = factory

    @switch_context
    def run_task(self, task=None, factory=None):
        logger.debug("%s starts %s", self, task)
        res = task.do_task()
        logger.debug("%s finished %s", self, task)
        factory.store(
            **{res.__class__.__name__.lower(): res}
        ) if res else None
        self.previous_task = task

        # put back the robot in the pool of free workers
        # for execution
        factory.free_robots.task_done()
        factory.free_robots.put(self)
