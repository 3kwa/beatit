"""A simple backend agnostic heartbeating convention"""

__version__ = "2022.3.1"

import time
import asyncio


class Heart:
    """
    >>> class Printer:
    ...     @staticmethod
    ...     def publish(*, subject, payload):
    ...         print(f"{payload} -> {subject}")
    >>> heart = Heart("my.process.identifier", publisher=Printer)
    >>> heart.__class__.__name__
    '_Sync'
    >>> class AsyncPrinter:
    ...     @staticmethod
    ...     async def publish(*, subject, payload):
    ...         print(f"{payload} -> {subject}")
    >>> heart = Heart("my.process.identifier", publisher=AsyncPrinter)
    >>> heart.__class__.__name__
    '_Async'
    >>> heart = Heart("my.process.identifier", publisher=Printer, subject_as_string=True)
    >>> heart.start(warmup=30)
    b'start/30' -> heartbeat.my.process.identifier
    """

    def __new__(cls, process, *, publisher, subject_as_string=False):
        if asyncio.iscoroutinefunction(publisher.publish):
            return _Async(process=process, publisher=publisher, subject_as_string=subject_as_string)
        else:
            return _Sync(process=process, publisher=publisher, subject_as_string=subject_as_string)


class _Sync:
    """
    >>> class Printer:
    ...     @staticmethod
    ...     def publish(*, subject, payload):
    ...         print(f"{payload} -> {subject}")
    >>> heart = _Sync(process="my.process.identifier", publisher=Printer)
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
    """

    def __init__(self, *, process, publisher, max_frequency=1, subject_as_string=False):
        self.process = process
        self.publisher = publisher
        self.max_frequency = max_frequency
        self._last_beat = 0
        self._last_degraded = 0
        self._subject = (
            f"heartbeat.{process}" if subject_as_string else f"heartbeat.{process}".encode()
        )

    def start(self, *, warmup):
        self._publish(f"start/{warmup}".encode())

    def stop(self):
        self._publish("stop".encode())
        # give the stop a chance to be published
        time.sleep(0.1)

    def degraded(self, *, period):
        now = time.time()
        if now - self._last_degraded >= self.max_frequency:
            self._last_degraded = now
            self._publish(f"degraded/{period}".encode())

    def beat(self, *, period):
        now = time.time()
        if now - self._last_beat >= self.max_frequency:
            self._last_beat = now
            self._publish(f"beat/{period}".encode())

    def _publish(self, message):
        self.publisher.publish(subject=self._subject, payload=message)


class _Async:
    """
    >>> class AsyncPrinter:
    ...     @staticmethod
    ...     async def publish(*, subject, payload):
    ...         print(f"{payload} -> {subject}")
    >>> heart = _Async(process="my.process.identifier", publisher=AsyncPrinter)
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
    """

    def __init__(self, *, process, publisher, max_frequency=1, subject_as_string=False):
        self.process = process
        self.publisher = publisher
        self.max_frequency = max_frequency
        self._last_beat = 0
        self._last_degraded = 0
        self._subject = (
            f"heartbeat.{process}" if subject_as_string else f"heartbeat.{process}".encode()
        )

    async def start(self, *, warmup):
        await self._publish(f"start/{warmup}".encode())

    async def stop(self):
        await self._publish("stop".encode())

    async def degraded(self, *, period):
        now = time.time()
        if now - self._last_degraded >= self.max_frequency:
            self._last_degraded = now
            await self._publish(f"degraded/{period}".encode())

    async def beat(self, *, period):
        now = time.time()
        if now - self._last_beat >= self.max_frequency:
            self._last_beat = now
            await self._publish(f"beat/{period}".encode())

    async def _publish(self, message):
        await self.publisher.publish(subject=self._subject, payload=message)
