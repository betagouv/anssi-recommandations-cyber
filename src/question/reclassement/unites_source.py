from schemas.albert import Paragraphe, UniteSource


def unites_du_paragraphe(paragraphe: Paragraphe) -> list[UniteSource]:
    if paragraphe.unites_source:
        return paragraphe.unites_source

    if not paragraphe.contenu.strip():
        return []

    return [UniteSource.depuis_paragraphe(paragraphe, paragraphe.contenu)]
