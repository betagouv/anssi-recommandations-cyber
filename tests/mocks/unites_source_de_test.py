from schemas.albert import UniteSource


def une_unite_source(
    contenu: str = "Une prescription",
    numero_page: int = 1,
    type_de_bloc: str = "paragraphe",
) -> UniteSource:
    return UniteSource(
        contenu=contenu,
        url="https://exemple.test/source.pdf",
        numero_page=numero_page,
        type_de_bloc=type_de_bloc,
    )


def une_table_des_matieres(
    contenu: str = "Sommaire", numero_page: int = 1
) -> UniteSource:
    return une_unite_source(contenu, numero_page, "table_des_matieres")
