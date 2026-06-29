import { writable } from 'svelte/store';

export type ValeurExactitude = 'Très bonne' | 'Bonne' | 'Correcte' | 'Fausse';
export type ValeurCompletude = Omit<ValeurExactitude, 'Fausse'> | 'Mauvaise';

export type Exactitude = {
  valeur: ValeurExactitude;
  commentaire?: string;
  precisionsInformationsErronees?: string;
  sourcesAdaptees?: string;
  erreurs?: Partial<Record<'informations-erronees' | 'sources-adaptees', string>>;
};
export type Completude = {
  valeur: ValeurCompletude;
  commentaire?: string;
  informationsManquantes?: string;
  sourcesAdaptees?: string;
  erreurs?: Partial<Record<'informations-manquantes' | 'sources-adaptees', string>>;
};
export type AvisUtilisateurBis = {
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
    let erreurInformationsErronees = undefined;
    if (precisions.trim().length > 5000) {
      erreurInformationsErronees =
        'Le champ `informations erronées` ne peut contenir que 5000 caractères maximum';
    }
    if (precisions.trim().length < 50) {
      erreurInformationsErronees =
        'Le champ `informations erronées` doit contenir au moins 50 caractères minimum';
    }

    const nouvelEtat = {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        precisionsInformationsErronees: precisions,
        ...(erreurInformationsErronees && {
          erreurs: {
            ...avisActuel.exactitude.erreurs,
            'informations-erronees': erreurInformationsErronees,
          },
        }),
      },
    };

    if (!erreurInformationsErronees) {
      delete nouvelEtat.exactitude.erreurs?.['informations-erronees'];
    }
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const indiqueLesSourcesAdapteesPourLExactitude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur !== 'Fausse') return avisActuel;
    let erreurSourcesAdaptees = undefined;
    if (sourcesAdaptees.trim().length > 5000) {
      erreurSourcesAdaptees =
        'Le champ `sources adaptées` ne peut contenir que 5000 caractères maximum';
    }
    if (sourcesAdaptees.trim().length < 50) {
      erreurSourcesAdaptees =
        'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum';
    }
    const nouvelEtat = {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        sourcesAdaptees: sourcesAdaptees,
        ...(erreurSourcesAdaptees && {
          erreurs: {
            ...avisActuel.exactitude.erreurs,
            'sources-adaptees': erreurSourcesAdaptees,
          },
        }),
      },
    };

    if (!erreurSourcesAdaptees) {
      delete nouvelEtat.exactitude.erreurs?.['sources-adaptees'];
    }
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
    let erreurInformationsManquantes = undefined;
    if (informationsManquantes.trim().length > 5000)
      erreurInformationsManquantes =
        'Le champ `informations manquantes` ne peut contenir que 5000 caractères maximum';
    if (informationsManquantes.trim().length < 50)
      erreurInformationsManquantes =
        'Le champ `informations manquantes` doit contenir au moins 50 caractères minimum';
    const nouvelEtat = {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        informationsManquantes: informationsManquantes,
        ...(erreurInformationsManquantes && {
          erreurs: {
            ...avisActuel.completude.erreurs,
            'informations-manquantes': erreurInformationsManquantes,
          },
        }),
      },
    };

    if (!erreurInformationsManquantes) {
      delete nouvelEtat.completude.erreurs?.['informations-manquantes'];
    }
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const indiqueLesSourcesAdapteesPourLaCompletude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur !== 'Mauvaise') return avisActuel;
    let erreurSourcesAdaptees = undefined;
    if (sourcesAdaptees.trim().length > 5000) {
      erreurSourcesAdaptees =
        'Le champ `sources adaptées` ne peut contenir que 5000 caractères maximum';
    }
    if (sourcesAdaptees.trim().length < 50) {
      erreurSourcesAdaptees =
        'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum';
    }
    const nouvelEtat = {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        sourcesAdaptees: sourcesAdaptees,
        ...(erreurSourcesAdaptees && {
          erreurs: {
            ...avisActuel.completude.erreurs,
            'sources-adaptees': erreurSourcesAdaptees,
          },
        }),
      },
    };

    if (!erreurSourcesAdaptees) {
      delete nouvelEtat.completude.erreurs?.['sources-adaptees'];
    }
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
    avisUtilisateurBis.exactitude.precisionsInformationsErronees.trim().length <=
      5000 &&
    avisUtilisateurBis.exactitude.precisionsInformationsErronees.trim().length >
      50 &&
    avisUtilisateurBis.exactitude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.exactitude.sourcesAdaptees.trim() !== '' &&
    avisUtilisateurBis.exactitude.sourcesAdaptees.trim().length <= 5000 &&
    avisUtilisateurBis.exactitude.sourcesAdaptees.trim().length > 50;
  const completudeAvecInformationsManquantesEtSourcesAdaptees =
    avisUtilisateurBis.completude.valeur === 'Mauvaise' &&
    avisUtilisateurBis.completude.informationsManquantes !== undefined &&
    avisUtilisateurBis.completude.informationsManquantes.trim() !== '' &&
    avisUtilisateurBis.completude.informationsManquantes.trim().length <= 5000 &&
    avisUtilisateurBis.completude.informationsManquantes.trim().length > 50 &&
    avisUtilisateurBis.completude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.completude.sourcesAdaptees?.trim() !== '' &&
    avisUtilisateurBis.completude.sourcesAdaptees.trim().length <= 5000 &&
    avisUtilisateurBis.completude.sourcesAdaptees.trim().length > 50;
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
