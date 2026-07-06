import { writable } from 'svelte/store';

export type ValeurPertinence =
  | 'Très pertinente'
  | 'Pertinente'
  | 'Correcte'
  | 'Erronée';
export type ValeurSourcesAdaptees =
  | 'Oui, tout à fait'
  | 'Oui, partiellement'
  | 'Non';

export type Pertinence = {
  valeur: ValeurPertinence;
  commentaire?: string;
  precisionsInformationsErronees?: string;
  erreurs?: Partial<Record<'informations-erronees', string>>;
};
export type SourcesAdaptees = {
  valeur: ValeurSourcesAdaptees;
  commentaire?: string;
  liste?: string;
  erreurs?: Partial<Record<'sources-adaptees', string>>;
};
export type AvisUtilisateurBis = {
  pertinence: Pertinence;
  sourcesAdaptees: SourcesAdaptees;
  idConversation: string;
  idInteraction: string;
  estValide: boolean;
};

const { subscribe, set, update } = writable<AvisUtilisateurBis>({
  pertinence: {} as Pertinence,
  sourcesAdaptees: {} as SourcesAdaptees,
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

const modifieLaValeurDesSourcesAdaptees = (valeur: ValeurSourcesAdaptees) => {
  update((avisActuel: AvisUtilisateurBis) => {
    const nouvelEtat = {
      ...avisActuel,
      sourcesAdaptees: { valeur },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const commenteLesSourcesAdaptees = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.sourcesAdaptees.valeur === 'Non') return avisActuel;
    const nouvelEtat = {
      ...avisActuel,
      sourcesAdaptees: { ...avisActuel.sourcesAdaptees, commentaire },
    };
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const indiqueLesSourcesAdaptees = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.sourcesAdaptees.valeur !== 'Non') return avisActuel;
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
      sourcesAdaptees: {
        ...avisActuel.sourcesAdaptees,
        liste: sourcesAdaptees,
        ...(erreurSourcesAdaptees && {
          erreurs: {
            ...avisActuel.sourcesAdaptees.erreurs,
            'sources-adaptees': erreurSourcesAdaptees,
          },
        }),
      },
    };

    if (!erreurSourcesAdaptees) {
      delete nouvelEtat.sourcesAdaptees.erreurs?.['sources-adaptees'];
    }
    return { ...nouvelEtat, estValide: estValide(nouvelEtat) };
  });
};

const estValide = (avisUtilisateurBis: AvisUtilisateurBis): boolean => {
  const pertinenceAvecOuSansCommentaire =
    avisUtilisateurBis.pertinence.valeur !== undefined &&
    avisUtilisateurBis.pertinence.valeur !== 'Erronée';
  const sourcesAdapteesAvecOuSansCommentaire =
    avisUtilisateurBis.sourcesAdaptees.valeur !== undefined &&
    avisUtilisateurBis.sourcesAdaptees.valeur !== 'Non';
  const pertinenceEtSourcesAdapteesAvecOuSansCommentaire =
    pertinenceAvecOuSansCommentaire && sourcesAdapteesAvecOuSansCommentaire;
  const pertinenceAvecInformationsErronees =
    avisUtilisateurBis.pertinence.valeur === 'Erronée' &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees !== undefined &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim() !== '' &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim().length <=
      5000 &&
    avisUtilisateurBis.pertinence.precisionsInformationsErronees.trim().length > 50;
  const sourcesAdaptees =
    avisUtilisateurBis.sourcesAdaptees.valeur === 'Non' &&
    avisUtilisateurBis.sourcesAdaptees.liste !== undefined &&
    avisUtilisateurBis.sourcesAdaptees.liste?.trim() !== '' &&
    avisUtilisateurBis.sourcesAdaptees.liste.trim().length <= 5000 &&
    avisUtilisateurBis.sourcesAdaptees.liste.trim().length > 50;
  return (
    pertinenceEtSourcesAdapteesAvecOuSansCommentaire ||
    (pertinenceAvecInformationsErronees &&
      (sourcesAdapteesAvecOuSansCommentaire || sourcesAdaptees)) ||
    (sourcesAdaptees &&
      (pertinenceAvecOuSansCommentaire || pertinenceAvecInformationsErronees))
  );
};

export const storeAvisUtilisateurBis = {
  subscribe,
  initialise: set,
  modifieLaValeurDeLaPertinence,
  modifieLaValeurDesSourcesAdaptees,
  commenteLaPertinence,
  commenteLesSourcesAdaptees,
  preciseLesInformationsErronees,
  indiqueLesSourcesAdaptees,
};
