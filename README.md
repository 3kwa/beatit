# beatit

A simple backend agnostic heartbeating convention.

```Python
>>> class Printer:
...     @staticmethod
...     def publish(*, subject: bytes, payload: bytes):
...         print(f"{payload} -> {subject}")
>>> from beatit import Heart
>>> heart = Heart(process="my.process.identifier", publisher=Printer)
>>> heart.start(warmup=60)
b'start/60' -> b'heartbeat.my.process.identifier'
>>> heart.beat(period=5)
b'beat/5' -> b'heartbeat.my.process.identifier'
>>> heart.beat(period=5)
>>> heart.degraded(period=5)
b'degraded/5' -> b'heartbeat.my.process.identifier'
>>> heart.degraded(period=5)
>>> heart.stop()
b'stop' -> b'heartbeat.my.process.identifier'

```

All you need is a publisher with a `publish` method accepting two named arguments `subject` and `payload`.

Instantiate a `Heart` instance with a `process` name and a `publisher`. *beats* will be published on the subject `heartbeat.<process>`.

What are the *beats*?

`start` with a `warmup` period (after which a `beat` or a `degraded` is expected)

`beat` with a `period` (when to expect the next `beat`).

`degraded` with a `period` (when to expect a `beat` or a `degraded` next).

`stop` when the process stops gracefully.

sync or not ...
---------------

If you favour async (what is wrong with you?) Heart recognizes an async publisher automagically and all you have to do is await all the things.

```Python
>>> import asyncio
>>> class AsyncPrinter:
...     @staticmethod
...     async def publish(*, subject: bytes, payload: bytes):
...         print(f"{payload} -> {subject}")
>>> from beatit import Heart
>>> heart = Heart(process="my.process.identifier", publisher=AsyncPrinter)
>>> asyncio.run(heart.start(warmup=60))
b'start/60' -> b'heartbeat.my.process.identifier'
>>> asyncio.run(heart.beat(period=5))
b'beat/5' -> b'heartbeat.my.process.identifier'
>>> asyncio.run(heart.beat(period=5))
>>> asyncio.run(heart.degraded(period=5))
b'degraded/5' -> b'heartbeat.my.process.identifier'
>>> asyncio.run(heart.degraded(period=5))
>>> asyncio.run(heart.stop())
b'stop' -> b'heartbeat.my.process.identifier'

```

`subject_as_string`
-------------------

`beatit` calls `publish` with `bytes` subject and payload. Seemed consistent but common publishers favour `str` for subject.

Fear not, here is a @limx0 approved solution!

```Python
>>> class StrBytes:
...     @staticmethod
...     def publish(*, subject: str, payload: bytes):
...         print(f"{payload} -> {subject}")
>>> from beatit import Heart
>>> heart = Heart(process="my.process.identifier", publisher=StrBytes, subject_as_string=True)
>>> heart.start(warmup=30)
b'start/30' -> heartbeat.my.process.identifier

```

