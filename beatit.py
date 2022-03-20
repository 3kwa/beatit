import time


class Heart:
    """
    >>> class Printer:
    ...     @staticmethod
    ...     def publish(subject, *, payload):
    ...         print(f"{payload} -> {subject}")
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
    """

    def __init__(self, *, process, publisher, max_frequency=1):
        self.process = process
        self.publisher = publisher
        self.max_frequency = max_frequency
        self._last_beat = 0
        self._last_degraded = 0

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
        self.publisher.publish(subject=f"heartbeat.{self.process}".encode(), payload=message)
