from concurrent.futures import Executor, Future, ThreadPoolExecutor
from typing import Callable, TypeVar
import threading

from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)

T = TypeVar("T")


class FutureAvecRappelRetarde(Future[T]):
    def __init__(
        self,
        rappel_demarre: threading.Event,
        liberation: threading.Event,
        lancer: Callable[[], None],
    ):
        super().__init__()
        self.rappel_demarre = rappel_demarre
        self.liberation = liberation
        self.lancer = lancer
        self._demarre = False

    def add_done_callback(self, fn) -> None:
        super().add_done_callback(fn)
        if not self._demarre:
            self._demarre = True
            self.lancer()

    def _invoke_callbacks(self) -> None:
        self.rappel_demarre.set()
        self.liberation.wait(timeout=5)
        getattr(super(), "_invoke_callbacks")()


class ExecuteurAvecRappelRetarde(Executor):
    def __init__(self) -> None:
        self.executeur = ThreadPoolExecutor(max_workers=2)
        self.rappel_demarre = threading.Event()
        self.liberation = threading.Event()
        self._premier = True

    def submit(self, fonction: Callable[..., T], /, *args, **kwargs) -> Future[T]:
        future: Future[T]

        def execute() -> None:
            if not future.set_running_or_notify_cancel():
                return
            try:
                future.set_result(fonction(*args, **kwargs))
            except BaseException as erreur:
                future.set_exception(erreur)

        if self._premier:

            def lancer() -> None:
                self.executeur.submit(execute)

            future = FutureAvecRappelRetarde(
                self.rappel_demarre,
                self.liberation,
                lancer,
            )
            self._premier = False
        else:
            future = Future()
            self.executeur.submit(execute)
        return future

    def shutdown(self, wait: bool = True, *, cancel_futures: bool = False) -> None:
        self.executeur.shutdown(wait=wait, cancel_futures=cancel_futures)


def test_reutilise_la_place_d_un_future_termine_avant_son_rappel() -> None:
    executeur = ExecuteurAvecRappelRetarde()
    coordinateur = CoordinateurReclassementParallele(
        executeur, nombre_maximum_d_appels_par_workflow=1
    )
    workflow = coordinateur.ouvre_workflow()
    try:
        premier = workflow.soumet(lambda: 1)
        assert executeur.rappel_demarre.wait(timeout=5)
        assert premier.done()
        assert premier.result() == 1
        second = workflow.soumet(lambda: 2)

        executeur.liberation.set()
        assert second.result(timeout=5) == 2
    finally:
        executeur.liberation.set()
        workflow.termine()
        coordinateur.ferme()
