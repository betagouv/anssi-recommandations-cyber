import { writable } from 'svelte/store';

export type ValeurExactitude = 'Très bonne' | 'Bonne' | 'Correcte' | 'Fausse';
export type ValeurCompletude = Omit<ValeurExactitude, 'Fausse'> | 'Mauvaise';

export type Exactitude = {
  valeur: ValeurExactitude;
  commentaire?: string;
  precisionsInformationsErronees?: string;
  sourcesAdaptees?: string;
};
export type Completude = {
  valeur: ValeurCompletude;
  commentaire?: string;
  informationsManquantes?: string;
  sourcesAdaptees?: string;
};
type AvisUtilisateurBis = {
  exactitude: Exactitude;
  completude: Completude;
  idConversation: string;
  idInteraction: string;
  estValide: boolean;
};

const { subscribe, set, update } = writable<AvisUtilisateurBis>({
  exactitude: {} as Exactitude,
  completude: {} as Completude,
  idConversation: '',
  idInteraction: '',
  estValide: false,
});

const modifieLaValeurDeLExactitude = (valeur: ValeurExactitude) => {
  update((avisActuel: AvisUtilisateurBis) => {
    const nouvelEtat = {
      ...avisActuel,
      exactitude: { valeur },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const commenteLExactitude = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur === 'Fausse') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      exactitude: { ...avisActuel.exactitude, commentaire },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const preciseLesInformationsErronees = (precisions: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur !== 'Fausse') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        precisionsInformationsErronees: precisions,
      },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const indiqueLesSourcesAdapteesPourLExactitude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur !== 'Fausse') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        sourcesAdaptees: sourcesAdaptees,
      },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const modifieLaValeurDeLaCompletude = (valeur: ValeurCompletude) => {
  update((avisActuel: AvisUtilisateurBis) => {
    const nouvelEtat = {
      ...avisActuel,
      completude: { valeur },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const commenteLaCompletude = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur === 'Mauvaise') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      completude: { ...avisActuel.completude, commentaire },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const preciseLesInformationsManquantes = (informationsManquantes: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur !== 'Mauvaise') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        informationsManquantes: informationsManquantes,
      },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const indiqueLesSourcesAdapteesPourLaCompletude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur !== 'Mauvaise') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        sourcesAdaptees: sourcesAdaptees,
      },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const estValide = (avisUtilisateurBis: AvisUtilisateurBis): boolean => {
  const exactitudeAvecOuSansCommentaire =
    avisUtilisateurBis.exactitude.valeur !== undefined &&
    avisUtilisateurBis.exactitude.valeur !== 'Fausse';
  const completudeAvecOuSansCommentaire =
    avisUtilisateurBis.completude.valeur !== undefined &&
    avisUtilisateurBis.completude.valeur !== 'Mauvaise';
  const exactitudeEtCompletudeAvecOuSansCommentaire =
    exactitudeAvecOuSansCommentaire && completudeAvecOuSansCommentaire;
  const exactitudeAvecInformationsErroneesEtSourcesAdaptees =
    avisUtilisateurBis.exactitude.valeur === 'Fausse' &&
    avisUtilisateurBis.exactitude.precisionsInformationsErronees !== undefined &&
    avisUtilisateurBis.exactitude.precisionsInformationsErronees.trim() !== '' &&
    avisUtilisateurBis.exactitude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.exactitude.sourcesAdaptees.trim() !== '';
  const completudeAvecInformationsManquantesEtSourcesAdaptees =
    avisUtilisateurBis.completude.valeur === 'Mauvaise' &&
    avisUtilisateurBis.completude.informationsManquantes !== undefined &&
    avisUtilisateurBis.completude.informationsManquantes.trim() !== '' &&
    avisUtilisateurBis.completude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.completude.sourcesAdaptees?.trim() !== '';
  return (
    exactitudeEtCompletudeAvecOuSansCommentaire ||
    (exactitudeAvecInformationsErroneesEtSourcesAdaptees &&
      (completudeAvecOuSansCommentaire ||
        completudeAvecInformationsManquantesEtSourcesAdaptees)) ||
    (completudeAvecInformationsManquantesEtSourcesAdaptees &&
      (exactitudeAvecOuSansCommentaire ||
        exactitudeAvecInformationsErroneesEtSourcesAdaptees))
  );
};

export const storeAvisUtilisateurBis = {
  subscribe,
  initialise: set,
  modifieLaValeurDeLExactitude,
  modifieLaValeurDeLaCompletude,
  commenteLExactitude,
  commenteLaCompletude,
  preciseLesInformationsErronees,
  indiqueLesSourcesAdapteesPourLExactitude,
  preciseLesInformationsManquantes,
  indiqueLesSourcesAdapteesPourLaCompletude,
};
