from __future__ import annotations

from typing import Callable, TYPE_CHECKING

# noinspection PyUnresolvedReferences
from PySide2.QtCore import QObject, QRunnable, Signal, Slot

if TYPE_CHECKING:
    pass


class Worker(QRunnable):
    """Worker thread for SCOUTS analysis. Avoids unresponsive GUI."""
    def __init__(self, func: Callable, *args, **kwargs) -> None:
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        """Run the Worker thread."""
        self.signals.started.emit()
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as error:
            self.signals.error.emit(error)
        else:
            self.signals.success.emit()
        finally:
            self.signals.finished.emit()


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread. Supported signals are:
         Started: Worker has begun working. Nothing is emitted.
         Finished: Worker has done executing (either naturally or by an Exception). Nothing is emitted.
         Success: Worker has finished executing without errors. Nothing is emitted.
         Error: an Exception was raised. Emits a Exception object.
         Aborted: the thread was aborted at some point. Nothing is emitted."""
    started = Signal()
    finished = Signal()
    success = Signal()
    error = Signal(Exception)
