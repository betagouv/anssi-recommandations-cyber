from concurrent.futures import Executor, Future
import threading
from typing import Callable, TypeVar

from configuration import CapaciteReclassementParallele

T = TypeVar("T")


class ErreurSaturationReclassement(RuntimeError):
    pass


class CoordinateurReclassementParallele:
    def __init__(
        self,
        executeur: Executor,
        capacite: CapaciteReclassementParallele = CapaciteReclassementParallele(),
    ) -> None:
        self.executeur = executeur
        self.capacite = capacite
        self._verrou = threading.Lock()
        self._workflows: set[WorkflowReclassement] = set()
        self._ferme = False

    def ouvre_workflow(self) -> "WorkflowReclassement":
        with self._verrou:
            if self._ferme:
                raise ErreurSaturationReclassement(
                    "Le reclassement parallèle est en cours de fermeture."
                )
            if len(self._workflows) >= self.capacite.nombre_maximum_de_workflows:
                raise ErreurSaturationReclassement(
                    "Le nombre maximal de reclassements simultanés est atteint."
                )
            workflow = WorkflowReclassement(self)
            self._workflows.add(workflow)
            return workflow

    def ferme(self) -> None:
        with self._verrou:
            self._ferme = True
        self.executeur.shutdown(wait=True, cancel_futures=True)

    def _libere(self, workflow: "WorkflowReclassement") -> None:
        with self._verrou:
            self._workflows.discard(workflow)


class WorkflowReclassement:
    def __init__(self, coordinateur: CoordinateurReclassementParallele) -> None:
        self._coordinateur = coordinateur
        self._verrou = threading.RLock()
        self._futures: set[Future] = set()
        self._termine = False

    def soumet(self, fonction: Callable[..., T], *arguments) -> Future[T]:
        with self._verrou:
            future = self._coordinateur.executeur.submit(fonction, *arguments)
            self._futures.add(future)
            future.add_done_callback(self._retire_future)
            return future

    def termine(self) -> None:
        with self._verrou:
            self._termine = True
            self._libere_si_possible()

    def _retire_future(self, future: Future) -> None:
        with self._verrou:
            self._futures.discard(future)
            self._libere_si_possible()

    def _libere_si_possible(self) -> None:
        if self._termine and not self._futures:
            self._coordinateur._libere(self)
