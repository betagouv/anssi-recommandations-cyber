import { writable } from "svelte/store";
import { tick } from "svelte";

type EtatAffichage = {
  enAttenteDeReponse: boolean;
};

const etatAffichageParDefaut: EtatAffichage = {
  enAttenteDeReponse: false,
};

const { subscribe, update } = writable<EtatAffichage>(etatAffichageParDefaut);

export const storeAffichage = {
  estEnAttenteDeReponse: (etat: boolean) => {
    update((etatActuel) => ({ ...etatActuel, enAttenteDeReponse: etat }));
  },
  scrollVersDernierMessage: async () => {
    await tick();
    const cibleScroll = document.getElementById("cible-scroll");
    if (cibleScroll)
      cibleScroll.scrollIntoView({ behavior: "smooth", block: "end" });
  },
  subscribe,
};
