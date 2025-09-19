from types import SimpleNamespace
from client_albert import ClientAlbert
from schemas.reponses import Paragraphe


def _creer_faux_captureur(captureur):
    def _fausse_creation(**kw):
        captureur["kwargs"] = kw
        msg = SimpleNamespace(content="ok")
        choix = SimpleNamespace(message=msg)
        return SimpleNamespace(choices=[choix])

    return _fausse_creation


def _setup_client(monkeypatch):
    c = object.__new__(ClientAlbert)
    monkeypatch.setattr(
        ClientAlbert,
        "recherche_paragraphes",
        lambda self, q: {
            "paragraphes": [
                Paragraphe(
                    score_similarite=0.9,
                    numero_page=0,
                    url="https://exemple/a",
                    nom_document="docA.pdf",
                    contenu="A",
                ),
                Paragraphe(
                    score_similarite=0.8,
                    numero_page=1,
                    url="https://exemple/b",
                    nom_document="docB.pdf",
                    contenu="B",
                ),
            ]
        },
    )
    captureur = {}
    c.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=_creer_faux_captureur(captureur))
        )
    )
    c.modele_reponse = "test-model"
    c.PROMPT_SYSTEM = "DEFAUT_PROMPT"
    return c, captureur


def test_pose_question_utilise_prompt_system_par_defaut(monkeypatch):
    c, captureur = _setup_client(monkeypatch)

    r = c.pose_question("Q sans surcharge")
    assert r.reponse == "ok"
    msgs = captureur["kwargs"]["messages"]
    assert msgs[0]["role"] == "system" and msgs[0]["content"] == "DEFAUT_PROMPT"


def test_pose_question_utilise_prompt_surcharge_quand_present(monkeypatch):
    c, captureur = _setup_client(monkeypatch)

    _ = c.pose_question("Quelle est la question ?", prompt_surcharge="SURCHARGE_X")
    kwargs = captureur["kwargs"]
    msgs = kwargs["messages"]
    assert msgs[0]["role"] == "system" and msgs[0]["content"] == "SURCHARGE_X"
