import json

from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees


def test_resoudre_retourne_la_reponse_pour_un_id_connu(tmp_path):
    mapping_path = tmp_path / "faq.mapping.json"
    mapping_path.write_text(
        json.dumps({"qui-est-le-directeur": "Vincent Strubel."}), encoding="utf-8"
    )
    mapping = MappingReponsesMaitrisees.depuis_chemin(mapping_path)

    assert mapping.resoudre("qui-est-le-directeur") == "Vincent Strubel."


def test_resoudre_retourne_none_pour_un_id_inconnu(tmp_path):
    mapping_path = tmp_path / "faq.mapping.json"
    mapping_path.write_text(json.dumps({}), encoding="utf-8")
    mapping = MappingReponsesMaitrisees.depuis_chemin(mapping_path)

    assert mapping.resoudre("id-inexistant") is None
