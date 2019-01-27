import functools
import logging
import queue
import threading
import time
import uuid


from settings import (
    TIME_FACTOR,
    ROBOT_PRICE_EUROS,
    ROBOT_PRICE_FOOS,
    FOOBAR_BATCH_SIZE,
    FOOBAR_QUANTITY_FOR_PRODUCTION,
    FOO_FACTORS,
)
from items import Robot
from tools import (
    MakeFoo, MakeBar,
    MakeFooBar, BuyRobot,
    SellFooBar,
)


logger = logging.getLogger(__name__)


def protect_with_lock(f):
    @functools.wraps(f)
    def wrap(obj, *args, **kwargs):
        logger.debug("Function %s%s tries to acquire lock", f, args)
        obj.lock.acquire(blocking=True)
        logger.debug("Function %s%s acquired lock", f, args)
        res = f(obj, *args, **kwargs)
        obj.lock.release()
        logger.debug("Function %s%s released lock.", f, args)
        return res

    return wrap


class FooBarFactory(object):
    """A thread-safe object for inventory and book-keeping."""

    FOOBAR_PRICE = 1  # euro
    ROBOT_PRICE = 3   # euro

    def __init__(self):
        self.foo_stack = []
        self.bar_stack = []
        self.foobar_stack = []
        self.money = 0
        self.uuid_pool = set()
        self.lock = threading.Lock()
        self.free_robots = queue.Queue()
        self.all_robots = [Robot(self), Robot(self)]
        self.free_robots = queue.Queue()
        [self.free_robots.put(r) for r in self.all_robots]

    @protect_with_lock
    def store(
        self,
        robot=None,
        foo=None,
        bar=None,
        foobar=None,
        money=None,
    ):
        # if you add something to the inventory, it must use this method only
        arguments = {
            'robot': robot, 'foo': foo,
            'bar': bar, 'foobar': foobar, 'money': money,
        }
        logger.debug("Storing %s", [v for v in arguments.values() if v])
        self.foo_stack.append(foo) if foo else None
        self.bar_stack.append(bar) if bar else None
        self.foobar_stack.append(foobar) if foobar else None
        self.free_robots.put(robot) if robot else None
        self.all_robots.append(robot) if robot else None
        self.money = self.money + (money if money else 0)

    def __get(self, name=None):
        """Warning: this must be protected with a lock to work."""
        try:
            return getattr(self, name + '_stack').pop()
        except IndexError:
            return

    @protect_with_lock
    def get_foo(self):
        return self.__get(name='foo')

    @protect_with_lock
    def get_bar(self):
        return self.__get(name='bar')

    @protect_with_lock
    def get_foobar(self):
        return self.__get(name='foobar')

    def get_foobar_sequence(self):
        foobar = self.get_foobar()
        sequence = []
        while foobar and len(sequence) < FOOBAR_BATCH_SIZE:
            sequence.append(foobar)
            foobar = self.get_foobar()

        return sequence

    def get_free_worker(self):
        """
        The application logic wants that this method
        will return a free robot in a blocking fashion,
        ie while no robot is free, the call blocks.

        A free robot returned is placed at the left of
        the deque. It is thus expected that if the last robot
        in the pool is busy, all the robots are busy too.
        """
        # the number of working robots should never exceed
        # the number of robots we have at hand
        return self.free_robots.get(block=True)

    @protect_with_lock
    def make_uuid(self):
        new_uuid = str(uuid.uuid4())
        while new_uuid in self.uuid_pool:
            new_uuid = str(uuid.uuid4())

        self.uuid_pool.add(new_uuid)
        return new_uuid

    @protect_with_lock
    def make_robot_uuid(self):
        return self._make_robot_uuid()

    def _make_robot_uuid(self):
        new_uuid = str(uuid.uuid4())[:4]
        while new_uuid in self.uuid_pool:
            new_uuid = str(uuid.uuid4())[:4]
        self.uuid_pool.add(new_uuid)
        return new_uuid

    def build_blocks(self, foo=None, bar=None):
        task_queue = (
            [
                MakeFoo(factory=self)
                for _ in range(foo)
            ] + [
                MakeBar(factory=self)
                for _ in range(bar)
            ]
        )
        self.empty_queue(task_queue)

    def start_robot(self, robot, task):
        th = threading.Thread(
            target=robot.run_task,
            kwargs={'task': task, 'factory': self}
        )
        th.start()

    def empty_queue(self, task_queue=None):
        while task_queue:
            task = task_queue.pop()
            robot = self.get_free_worker()  # blocking call
            self.start_robot(robot, task)

    def build_foobars(self):
        foo = self.get_foo()
        bar = self.get_bar()
        while foo and bar:
            self.start_robot(
                self.get_free_worker(),
                MakeFooBar(factory=self, foo=foo, bar=bar)
            )
            foo = self.get_foo()
            bar = self.get_bar()
        else:
            # put back material in the store
            if foo:
                self.store(foo=foo)
            if bar:
                self.store(bar=bar)

    def sell_foobars(self):
        foobar_sequence = self.get_foobar_sequence()
        while foobar_sequence:
            self.start_robot(
                self.get_free_worker(),
                SellFooBar(factory=self, foobar_sequence=foobar_sequence)
            )
            foobar_sequence = self.get_foobar_sequence()

    @protect_with_lock
    def buy_robot(self):
        if (
            self.money >= ROBOT_PRICE_EUROS
            and len(self.foo_stack) > ROBOT_PRICE_FOOS
        ):
            self.money = self.money - ROBOT_PRICE_EUROS
            [self.foo_stack.pop() for x in range(ROBOT_PRICE_FOOS)]
            return Robot(factory=self, uuid=self._make_robot_uuid())

    def buy_robots(self):
        robot = self.buy_robot()
        while robot:
            buyer_robot = self.get_free_worker()
            self.start_robot(
                robot=buyer_robot,
                task=BuyRobot(factory=self, robot=robot)
            )
            robot = self.buy_robot()

    def log_stock(self):
        logger.info(
            "foo's=%s, bar's=%s, foobar's=%s, "
            "money=%s€, all robots=%s, free robots=%s",
            len(self.foo_stack), len(self.bar_stack),
            len(self.foobar_stack), self.money, len(self.all_robots),
            self.free_robots.qsize()
        )

    def run(self):
        logger.info(
            "Start launching foobar factory with time speed = %s×",
            TIME_FACTOR
        )
        while True and len(self.all_robots) < 100:
            self.log_stock()
            staff_factor = (len(self.all_robots) // 4 + 1)
            foo_to_build = int(
                FOOBAR_QUANTITY_FOR_PRODUCTION * FOO_FACTORS * staff_factor
            )
            bar_to_build = int(FOOBAR_QUANTITY_FOR_PRODUCTION * staff_factor)
            logger.info(
                "start building %s foo and %s bars".center(78, '-'),
                foo_to_build, bar_to_build
            )
            # make a bunch of foo and bars
            self.build_blocks(foo=foo_to_build, bar=bar_to_build)
            self.log_stock()
            logger.info("start building foobars".center(80, '-'))
            self.build_foobars()               # build foobars from parts
            self.log_stock()
            logger.info("start selling foobars".center(80, '-'))
            self.sell_foobars()                # get the money
            self.log_stock()
            logger.info("start buying robots".center(80, '-'))
            self.buy_robots()     # improve staff
        else:
            self.wait_for_threads()

    def wait_for_threads(self):
        logger.info("End of the simulation".center(80, '-'))
        logger.info("Wait for all the threads to terminate".center(80, '-'))
        total_robots = len(self.all_robots)
        free_workers = self.free_robots.qsize()
        while total_robots != free_workers:
            logger.info(
                "%s robots are at rest, total of staff is %s",
                free_workers, total_robots
            )
            self.log_stock()
            total_robots = len(self.all_robots)
            free_workers = self.free_robots.qsize()
            time.sleep(10 / TIME_FACTOR)

        logger.info("End of the execution")
        self.log_stock()
