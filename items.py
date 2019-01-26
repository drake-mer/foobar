class Foo():
    def __init__(self, factory=None):
        self.uuid = factory.make_uuid()
        

class Bar():
    def __init__(self, factory):
        self.uuid = factory.make_uuid()


class FooBar():
    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar


class Robot():
    def __init__(self):
        self.tasks = []

    def give_task(self, task):
        self.tasks.append(task)
    
    def run_task(self, factory=None):
        task_to_perform = self.tasks.pop()
        res = task_to_perform.do_task()
        factory.store(res) if res else None
