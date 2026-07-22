import type { ReponseParagraphe } from '../../src/client.api';

class ConstructeurDeParagraphe {
  construis(): ReponseParagraphe {
    return {
      contenu: 'Un contenu',
      nom_document: 'Un document',
      numero_page: 12,
      url: 'http://mqc.local',
      titre: 'Un titre',
      date_mise_a_jour: '2026-07-12T21:23:00:000Z',
    };
  }
}

export const unConstructeurParagraphe = () => new ConstructeurDeParagraphe();
