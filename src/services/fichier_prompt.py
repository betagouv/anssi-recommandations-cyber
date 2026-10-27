from pathlib import Path


def lis_fichier_prompt(nom_fichier_prompt: str) -> str:
    template_path = Path.cwd() / "templates" / nom_fichier_prompt
    return template_path.read_text(encoding="utf-8")
