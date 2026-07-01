import { Paragraphe } from '../../src/stores/conversation.store';

class ConstructeurDeParagraphe {
  construis(): Paragraphe {
    return {
      contenu: 'Un contenu',
      nom_document: 'Un document',
      numero_page: 12,
      url: 'http://mqc.local',
    };
  }
}

export const unConstructeurParagraphe = () => new ConstructeurDeParagraphe();
