import re

from schemas.albert import Paragraphe, UniteSource


_FRONTIERE_PARAGRAPHE = re.compile(r"\r?\n[ \t]*\r?\n(?:[ \t]*\r?\n)*")


def unites_du_paragraphe(paragraphe: Paragraphe) -> list[UniteSource]:
    if paragraphe.unites_source:
        return paragraphe.unites_source

    return [
        UniteSource(
            contenu=contenu,
            url=paragraphe.url,
            numero_page=paragraphe.numero_page,
            nom_document=paragraphe.nom_document,
            type_de_bloc=paragraphe.type_de_bloc,
            code_recommandation=paragraphe.code_recommandation,
            chemin_sections=paragraphe.chemin_sections,
            position_page=paragraphe.position_page,
            derniere_page=paragraphe.derniere_page,
            identifiant_document=paragraphe.identifiant_document,
        )
        for contenu in _FRONTIERE_PARAGRAPHE.split(paragraphe.contenu)
        if contenu.strip()
    ]


def premiere_unite_substantielle(
    unites: list[UniteSource], debut: int, fin: int
) -> UniteSource | None:
    return next(
        (
            unite
            for unite in unites[debut - 1 : fin]
            if unite.type_de_bloc != "table_des_matieres"
        ),
        None,
    )
