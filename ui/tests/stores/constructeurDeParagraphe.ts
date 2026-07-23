import type { ReponseParagraphe } from '../../src/client.api';

class ConstructeurDeParagraphe {
  private _urlDocument: string = 'http://mqc.local';

  avecURLDocument(urlDocument: string): ConstructeurDeParagraphe {
    this._urlDocument = urlDocument;
    return this;
  }

  construis(): ReponseParagraphe {
    return {
      contenu: 'Un contenu',
      nom_document: 'Un document',
      numero_page: 12,
      url: this._urlDocument,
      titre: 'Un titre',
      date_mise_a_jour: '2026-07-12T21:23:00:000Z',
    };
  }
}

export const unConstructeurParagraphe = () => new ConstructeurDeParagraphe();
