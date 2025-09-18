from __future__ import annotations
import pytest
from managers.manager_historique import ManagerHistorique
from managers.manager_historique_concatenation import ManagerHistoriqueConcatenation


def test_manager_historique_abstrait_ne_peut_pas_etre_instancie() -> None:
    with pytest.raises(TypeError):
        ManagerHistorique()


def test_manager_concatenation_recuperer_messages_retourne_liste_vide() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()
    messages = gestionnaire.recuperer_messages()
    assert len(messages) == 0


def test_manager_concatenation_recuperer_messages_retourne_liste_un_element() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()
    gestionnaire._messages = [{"role": "user", "content": "Première question ?"}]
    messages = gestionnaire.recuperer_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Première question ?"


def test_manager_concatenation_ajoute_un_messages_assistant() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()
    assert gestionnaire.recuperer_messages() == []

    gestionnaire.ajoute_message_assistant("Première question ?")
    messages = gestionnaire.recuperer_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] == "Première question ?"


def test_manager_concatenation_ajoute_un_messages_utilisateur() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()
    assert gestionnaire.recuperer_messages() == []

    gestionnaire.ajoute_message_utilisateur("Première question ?")
    messages = gestionnaire.recuperer_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Première question ?"


def test_manager_concatenation_recupere_un_message_assistant() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()

    gestionnaire.ajoute_message_assistant("Reponse 1")
    messages = gestionnaire.recuperer_messages()

    assert len(messages) == 1
    assert messages[0] == {"role": "assistant", "content": "Reponse 1"}


def test_manager_concatenation_recupere_un_message_utilisateur() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()

    gestionnaire.ajoute_message_utilisateur("Reponse 1")
    messages = gestionnaire.recuperer_messages()

    assert len(messages) == 1
    assert messages[0] == {"role": "user", "content": "Reponse 1"}


def test_manager_concatenation_recupere_deux_messages_assistant() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()

    gestionnaire.ajoute_message_assistant("Reponse 1")
    gestionnaire.ajoute_message_assistant("Reponse 2")
    messages = gestionnaire.recuperer_messages()

    assert len(messages) == 2
    assert messages[1] == {"role": "assistant", "content": "Reponse 2"}


def test_manager_concatenation_recupere_deux_messages_utilisateur() -> None:
    gestionnaire = ManagerHistoriqueConcatenation()

    gestionnaire.ajoute_message_utilisateur("Reponse 1")
    gestionnaire.ajoute_message_utilisateur("Reponse 2")
    messages = gestionnaire.recuperer_messages()

    assert len(messages) == 2
    assert messages[1] == {"role": "user", "content": "Reponse 2"}
