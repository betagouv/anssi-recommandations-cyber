import { describe, expect, it } from 'vitest';
import { get } from 'svelte/store';
import { storeTags } from '../../src/stores/tags.store';
import { storeConversation } from '../../src/stores/conversation.store';

describe('Le store des tags', () => {
  it('retourne les tags par défaut', () => {
    const tags = get(storeTags);

    expect(tags.positifs()).toEqual([
      {
        label: 'Facile à comprendre',
        id: 'facileacomprendre',
      },
      {
        label: 'Complète',
        id: 'complete',
      },
      {
        label: 'Bien structurée',
        id: 'bienstructuree',
      },
      {
        label: 'Sources utiles',
        id: 'sourcesutiles',
      },
    ]);
    expect(tags.negatifs()).toEqual([
      {
        label: 'Pas assez détaillée',
        id: 'pasassezdetaillee',
      },
      {
        label: 'Trop complexe',
        id: 'tropcomplexe',
      },
      {
        label: 'Sources peu utiles',
        id: 'sourcespeuutiles',
      },
      {
        label: 'Information erronée',
        id: 'informationerronee',
      },
      {
        label: 'Hors sujet',
        id: 'horssujet',
      },
    ]);
  });

  it('ajoute le tag conversation si la conversation contient plus de 2 interactions', function () {
    storeConversation.initialise({
      messages: [
        {
          contenu: 'Première question ?',
          emetteur: 'utilisateur',
        },
        {
          contenu: 'Deuxième question ?',
          emetteur: 'utilisateur',
        },
      ],
      derniereQuestion: 'La dernière question ?',
      idConversation: 'un-conversation-id',
    });

    const tags = get(storeTags);

    expect(tags.positifs()[0]).toStrictEqual({
      label: 'Conversation',
      id: 'conversation',
      icon: 'speak-line',
    });
    expect(tags.negatifs()[0]).toStrictEqual({
      label: 'Conversation',
      id: 'conversation',
      icon: 'speak-line',
    });
  });
});
