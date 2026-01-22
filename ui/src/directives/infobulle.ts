export const infobulle = (noeud: HTMLElement, contenu: string) => {
  const elementInfobulle = document.createElement("div");
  const elementContenuInfobulle = document.createElement("p");
  elementInfobulle.classList.add("conteneur-infobulle");
  elementContenuInfobulle.textContent = contenu;
  elementInfobulle.appendChild(elementContenuInfobulle);
  document.body.appendChild(elementInfobulle);

  const estVisible = () => elementInfobulle.style.display === "flex";

  const positionne = () => {
    const { top, left, width } = noeud.getBoundingClientRect();
    const tailleInfobulle = elementInfobulle.getBoundingClientRect();
    elementInfobulle.style.top = `${top - tailleInfobulle.height - 12}px`;
    elementInfobulle.style.left = `${left - tailleInfobulle.width / 2 + width / 2}px`;
  };

  const affiche = () => {
    elementInfobulle.style.display = "flex";
    positionne();
  };

  const masque = () => {
    elementInfobulle.style.display = "none";
  };

  const surEntree = (e: PointerEvent) => {
    if (e.pointerType === "mouse") affiche();
  };
  const surSortie = (e: PointerEvent) => {
    if (e.pointerType === "mouse") masque();
  };

  const surTapNoeud = (e: PointerEvent) => {
    if (e.pointerType === "mouse") return;
    if (estVisible()) masque();
    else affiche();
  };

  const surTapAilleurs = (e: PointerEvent) => {
    const cible = e.target as Node | null;
    if (estVisible() && cible && !noeud.contains(cible)) masque();
  };

  const surScrollOuBlur = () => masque();
  const surCancel = () => masque();

  noeud.addEventListener("pointerenter", surEntree);
  noeud.addEventListener("pointerleave", surSortie);
  noeud.addEventListener("pointerdown", surTapNoeud);

  document.addEventListener("pointerdown", surTapAilleurs, { passive: true });
  window.addEventListener("scroll", surScrollOuBlur, { passive: true });
  window.addEventListener("blur", surScrollOuBlur);
  window.addEventListener("pointercancel", surCancel);

  return {
    destroy() {
      noeud.removeEventListener("pointerenter", surEntree);
      noeud.removeEventListener("pointerleave", surSortie);
      noeud.removeEventListener("pointerdown", surTapNoeud);

      document.removeEventListener("pointerdown", surTapAilleurs);
      window.removeEventListener("scroll", surScrollOuBlur);
      window.removeEventListener("blur", surScrollOuBlur);
      window.removeEventListener("pointercancel", surCancel);

      elementInfobulle.remove();
    },
  };
};
