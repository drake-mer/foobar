import functools

from .settings import TIME_FACTOR
from .items import (
    Robot, Foo, Bar, FooBar
)


def spend_time(f):
    @functools.wraps
    def wrapper(obj, *args, **kwargs):
        time.sleep(obj.time_needed * TIME_FACTOR)
        return f(obj, *args, **kwargs)
    return wrapper


class TaskMixin(object):
    def __init__(
        self,
        time_needed=None,
        product_type=None,
        factory=None,
    ):
        self.time_needed = time_needed
        self.cls = product_type
        self.factory = factory
   
    @spend_time
    def do_task(factory=None):
        """This is the default implementation."""
        (factory or self.factory).store(
            **{self.cls.__name__: self.cls()}
        )


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


class MakeRobot(TaskMixin):
    def __init__(self, factory=None):
        super(MakeRobot, self).__init__(
            time_needed=0,
            product_type=Robot,
            factory=factory,
        )

    @spend_time
    def do_task(factory=None):
        factory = factory or self.factory
        if factory.can_make_robot():
            robot = factory.do_robot()
            factory.store(robot=robot)
        else:
            raise ValueError(
                "You can't produce a robot: stock is too low;"
                "money={}, foo={}".format(MONEY, len(FOO_STACK))            )


class MakeFooBar(TaskMixin):
    def __init__(self, factory=None):
        super(MakeFooBar, self).__init__(
            time_needed=2.,
            product_type=FooBar,
            factory=factory
        )

    @spend_time
    def do_task(factory=None):
        factory = factory or self.factory
        foo = factory.get_foo()
        bar = factory.get_bar()
        if random.random() > 0.4:
            factory.store(foobar=FooBar(foo, bar))
        else:
            factory.store(bar=bar)


class SellFooBar(TaskMixin):
    def __init__(self, factory=None):
        super(SellFooBar, self).__init__(
            time_needed=10.,
            factory=factory
        )

    @spend_time
    def do_task(self, factory=None):
        to_sell = []
        factory = factory or self.factory
        while factory.has_foobar():
            to_sell.append(factory.get_foobar())

        factory.store(money=len(to_sell))
        print(
            "We just sold {} foobars".format(
                len(stock_to_sell)
            )
        )

