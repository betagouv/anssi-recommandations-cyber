import { writable } from 'svelte/store';

export type ValeurPertinence =
  | 'Très pertinente'
  | 'Pertinente'
  | 'Correcte'
  | 'Erronée';
export type ValeurCompletude = Omit<ValeurPertinence, 'Fausse'> | 'Mauvaise';

export type Pertinence = {
  valeur: ValeurPertinence;
  commentaire?: string;
  precisionsInformationsErronees?: string;
  erreurs?: Partial<Record<'informations-erronees', string>>;
};
export type Completude = {
  valeur: ValeurCompletude;
  commentaire?: string;
  informationsManquantes?: string;
  sourcesAdaptees?: string;
  erreurs?: Partial<Record<'informations-manquantes' | 'sources-adaptees', string>>;
};
export type AvisUtilisateurBis = {
  pertinence: Pertinence;
  completude: Completude;
  idConversation: string;
  idInteraction: string;
  estValide: boolean;
};

const { subscribe, set, update } = writable<AvisUtilisateurBis>({
  pertinence: {} as Pertinence,
  completude: {} as Completude,
  idConversation: '',
  idInteraction: '',
  estValide: false,
});

const modifieLaValeurDeLaPertinence = (valeur: ValeurPertinence) => {
  update((avisActuel: AvisUtilisateurBis) => {
    const nouvelEtat = {
      ...avisActuel,
      pertinence: { valeur },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const commenteLaPertinence = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.pertinence.valeur === 'Erronée') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      pertinence: { ...avisActuel.pertinence, commentaire },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const preciseLesInformationsErronees = (precisions: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.pertinence.valeur !== 'Erronée') return avisActuel;
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
      pertinence: {
        ...avisActuel.pertinence,
        precisionsInformationsErronees: precisions,
        ...(erreurInformationsErronees && {
          erreurs: {
            'informations-erronees': erreurInformationsErronees,
          },
        }),
      },
    };

    if (!erreurInformationsErronees) {
      delete nouvelEtat.pertinence.erreurs?.['informations-erronees'];
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
  const pertinenceAvecOuSansCommentaire =
    avisUtilisateurBis.pertinence.valeur !== undefined &&
    avisUtilisateurBis.pertinence.valeur !== 'Erronée';
  const completudeAvecOuSansCommentaire =
    avisUtilisateurBis.completude.valeur !== undefined &&
    avisUtilisateurBis.completude.valeur !== 'Mauvaise';
  const pertinenceEtCompletudeAvecOuSansCommentaire =
    pertinenceAvecOuSansCommentaire && completudeAvecOuSansCommentaire;
  const pertinenceAvecInformationsErronees =
    avisUtilisateurBis.pertinence.valeur === 'Erronée' &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees !== undefined &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim() !== '' &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim().length <=
      5000 &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim().length > 50;
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
    pertinenceEtCompletudeAvecOuSansCommentaire ||
    (pertinenceAvecInformationsErronees &&
      (completudeAvecOuSansCommentaire ||
        completudeAvecInformationsManquantesEtSourcesAdaptees)) ||
    (completudeAvecInformationsManquantesEtSourcesAdaptees &&
      (pertinenceAvecOuSansCommentaire || pertinenceAvecInformationsErronees))
  );
};

export const storeAvisUtilisateurBis = {
  subscribe,
  initialise: set,
  modifieLaValeurDeLaPertinence,
  modifieLaValeurDeLaCompletude,
  commenteLaPertinence,
  commenteLaCompletude,
  preciseLesInformationsErronees,
  preciseLesInformationsManquantes,
  indiqueLesSourcesAdapteesPourLaCompletude,
};
