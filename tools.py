import logging
import random

from settings import (
    FOOBAR_PRICE,
)
from mixins import (
    TaskMixin,
    spend_time,
)
from items import (
    Robot, Foo,
    Bar, FooBar,
)


logger = logging.getLogger(__name__)


class MakeFoo(TaskMixin):
    def __init__(self, factory=None):
        super(MakeFoo, self).__init__(
            time_needed=1.,
            product_type=Foo,
            factory=factory,
        )


class MakeBar(TaskMixin):
    def __init__(self, factory=None):
        super(MakeBar, self).__init__(
            time_needed=random.random() * 1.5 + 0.5,
            product_type=Bar,
            factory=factory,
        )


class BuyRobot(TaskMixin):
    def __init__(self, factory=None, robot=None):
        super(BuyRobot, self).__init__(
            time_needed=0,
            product_type=Robot,
            factory=factory,
        )
        self.robot = robot

    @spend_time
    def do_task(self):
        self.factory.store(robot=self.robot)


class MakeFooBar(TaskMixin):
    def __init__(self, factory=None, foo=None, bar=None):
        super(MakeFooBar, self).__init__(
            time_needed=2.,
            product_type=FooBar,
            factory=factory
        )
        self.foo = foo
        self.bar = bar

    @spend_time
    def do_task(self, factory=None):
        factory = factory or self.factory
        bar = self.bar
        foo = self.foo
        if random.random() > 0.4:
            factory.store(
                foobar=FooBar(
                    factory=factory,
                    uuid=self.uuid,
                    foo=foo, bar=bar,
                )
            )
        else:
            # put back the bar in our stocks
            factory.store(bar=bar)


class SellFooBar(TaskMixin):
    def __init__(self, foobar_sequence=None, factory=None):
        super(SellFooBar, self).__init__(
            time_needed=10.,
            factory=factory
        )
        self.foobar_sequence = foobar_sequence

    @spend_time
    def do_task(self, factory=None):
        factory = factory or self.factory
        factory.store(money=FOOBAR_PRICE * len(self.foobar_sequence))
        logger.debug(
            "{} foobars have been sold".format(len(self.foobar_sequence))
        )
