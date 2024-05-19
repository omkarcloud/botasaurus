from threading import Thread

class ThreadWithResult(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None
    ):
        self.result = None
        self._exception = None

        def function():
            try:
                self.result = target(*args, **kwargs)
            except Exception as e:
                self._exception = e

        super().__init__(group=group, target=function, name=name, daemon=daemon)

    def join(self, timeout=None):
        super().join(timeout)
        if self._exception:
            raise self._exception