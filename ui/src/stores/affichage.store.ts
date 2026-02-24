import { writable } from 'svelte/store';
import { tick } from 'svelte';

type EtatAffichage = {
  enAttenteDeReponse: boolean;
  aUneErreurAlbert: boolean;
  messageErreurAlbert: string;
};

const etatAffichageParDefaut: EtatAffichage = {
  enAttenteDeReponse: false,
  aUneErreurAlbert: false,
  messageErreurAlbert: '',
};

const { subscribe, update } = writable<EtatAffichage>(etatAffichageParDefaut);

export const storeAffichage = {
  estEnAttenteDeReponse: (etat: boolean) => {
    update((etatActuel) => ({ ...etatActuel, enAttenteDeReponse: etat }));
  },
  erreurAlbert: (estEnErreur: boolean, message: string = '') => {
    update((etatActuel) => ({
      ...etatActuel,
      aUneErreurAlbert: estEnErreur,
      messageErreurAlbert: estEnErreur ? message : '',
    }));
  },
  scrollVersDernierMessage: async () => {
    await tick();
    const cibleScroll = document.getElementById('cible-scroll');
    if (cibleScroll)
      cibleScroll.scrollIntoView({ behavior: 'smooth', block: 'end' });
  },
  subscribe,
};
