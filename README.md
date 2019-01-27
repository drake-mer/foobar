# How to run this program?

In the source directory, execute:
```
python3 run.py
```

# What does this program?

It simulate the production of `foo` and `bar` by robots
in a factory with a given set of constraints.

The basic algorithm to produce `foo`, `bar` and robots
is illustrated in the `factory` module,
in the `FooBarFactory.run` method.

We start building the elementary bricks (`foo` and `bar` objects),
then we assemble
them, then we sell them, and with the gain we buy new robots.

We repeat this operation while amplifying the production
at each round, because of the more important workforce.

# How can you modify the settings?

You can edit the `settings.py` file, which has, hopefully,
enough comments.

If you want to make the log really verbose, replace the `'INFO'`
string by a `'DEBUG'` string in the logging dict config, or conversely
replace `'INFO'` by `'DEBUG'` if you want all the infos.

An interesting setting is the `TIME_FACTOR` constants, that will
accelerate the time elapsing (set it to 10 to reduce all the waiting
times by a factor of 10).

# How does this program work?

It basically run threads that are executed for a given amount 
of time. A worker pool contains the set of all the free robots
that can be given a task. When a worker finishes his work,
he put itself back in the worker pool.

All the data (stock, inventory, etc) are stored in the FooBarFactory
state object.
