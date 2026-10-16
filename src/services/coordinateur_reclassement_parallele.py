from concurrent.futures import Executor, Future
import threading
from typing import Callable, TypeVar


T = TypeVar("T")


class ErreurSaturationReclassement(RuntimeError):
    pass


class CoordinateurReclassementParallele:
    def __init__(
        self,
        executeur: Executor,
        nombre_maximum_de_workflows: int = 2,
        nombre_maximum_d_appels_par_workflow: int = 5,
        nombre_maximum_de_candidats: int | None = None,
    ) -> None:
        if (
            type(nombre_maximum_de_workflows) is not int
            or nombre_maximum_de_workflows < 1
        ):
            raise ValueError("Le nombre maximal de workflows doit être positif.")
        if (
            type(nombre_maximum_d_appels_par_workflow) is not int
            or nombre_maximum_d_appels_par_workflow < 1
        ):
            raise ValueError("La capacité d'appels du workflow doit être positive.")
        if nombre_maximum_de_candidats is not None and (
            type(nombre_maximum_de_candidats) is not int
            or nombre_maximum_de_candidats < 1
        ):
            raise ValueError("La capacité de candidats doit être positive.")
        self.executeur = executeur
        self.nombre_maximum_de_workflows = nombre_maximum_de_workflows
        self.nombre_maximum_d_appels_par_workflow = nombre_maximum_d_appels_par_workflow
        self.nombre_maximum_de_candidats = nombre_maximum_de_candidats
        self._verrou = threading.Lock()
        self._workflows: set[WorkflowReclassement] = set()
        self._ferme = False

    def ouvre_workflow(self) -> "WorkflowReclassement":
        with self._verrou:
            if self._ferme:
                raise ErreurSaturationReclassement(
                    "Le reclassement parallèle est en cours de fermeture."
                )
            if len(self._workflows) >= self.nombre_maximum_de_workflows:
                raise ErreurSaturationReclassement(
                    "Le nombre maximal de reclassements simultanés est atteint."
                )
            workflow = WorkflowReclassement(self)
            self._workflows.add(workflow)
            return workflow

    def ferme(self) -> None:
        with self._verrou:
            if self._ferme:
                return
            self._ferme = True
            workflows = list(self._workflows)
        for workflow in workflows:
            workflow.annule_en_attente()
            workflow.termine()
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
        self._libere = False
        self._erreur: BaseException | None = None

    @property
    def nombre_maximum_d_appels(self) -> int:
        return self._coordinateur.nombre_maximum_d_appels_par_workflow

    @property
    def nombre_maximum_de_candidats(self) -> int | None:
        return self._coordinateur.nombre_maximum_de_candidats

    def soumet(self, fonction: Callable[..., T], *arguments) -> Future[T]:
        with self._verrou:
            if self._termine:
                raise RuntimeError("Le workflow de reclassement est terminé.")
            for future in tuple(self._futures):
                if future.done():
                    self._retire_future(future)
            self._verifie_echec()
            if (
                len(self._futures)
                >= self._coordinateur.nombre_maximum_d_appels_par_workflow
            ):
                raise RuntimeError("Trop d'appels simultanés pour ce reclassement.")
            future = self._coordinateur.executeur.submit(fonction, *arguments)
            self._futures.add(future)
            future.add_done_callback(self._retire_future)
            return future

    def annule_en_attente(self) -> None:
        with self._verrou:
            futures = list(self._futures)
        for future in futures:
            future.cancel()

    def verifie_succes(self) -> None:
        with self._verrou:
            self._verifie_echec()

    def termine(self) -> None:
        with self._verrou:
            self._termine = True
            self._libere_si_possible()

    def _retire_future(self, future: Future) -> None:
        with self._verrou:
            if not future.cancelled():
                self._erreur = future.exception() or self._erreur
            self._futures.discard(future)
            self._libere_si_possible()

    def _verifie_echec(self) -> None:
        if self._erreur is not None:
            raise self._erreur
        for future in self._futures:
            if future.done() and not future.cancelled():
                erreur = future.exception()
                if erreur is not None:
                    self._erreur = erreur
                    raise erreur

    def _libere_si_possible(self) -> None:
        if self._termine and not self._futures and not self._libere:
            self._libere = True
            self._coordinateur._libere(self)
