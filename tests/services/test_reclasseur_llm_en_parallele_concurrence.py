from concurrent.futures import Executor, Future, ThreadPoolExecutor

import pytest

from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)


class ExecuteurSynchrone(Executor):
    def submit(self, fn, /, *args, **kwargs):
        future: Future = Future()
        future.set_result(fn(*args, **kwargs))
        return future


def test_garde_sa_place_jusqu_a_la_fin_du_reclassement() -> None:
    coordinateur = CoordinateurReclassementParallele(ExecuteurSynchrone())
    workflow = coordinateur.ouvre_workflow()
    workflow.soumet(int)
    coordinateur.ouvre_workflow()

    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()

    workflow.termine()
    coordinateur.ouvre_workflow()


def test_la_fermeture_arrete_l_executeur_et_refuse_de_nouveaux_reclassements() -> None:
    executeur = ThreadPoolExecutor(max_workers=1)
    coordinateur = CoordinateurReclassementParallele(executeur)

    coordinateur.ferme()

    with pytest.raises(RuntimeError):
        executeur.submit(int)
    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()
