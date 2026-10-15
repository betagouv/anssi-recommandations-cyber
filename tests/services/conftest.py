
import pytest
from concurrent.futures import ThreadPoolExecutor

from services.coordinateur_reclassement_parallele import CoordinateurReclassementParallele


@pytest.fixture()
def un_coordinateur_reclassement():
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=5))
    yield coordinateur
    coordinateur.ferme()
