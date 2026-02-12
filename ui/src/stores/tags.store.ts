import { derived } from 'svelte/store';
import { storeConversation } from './conversation.store';

const TAGS_POSITIFS = [
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
];
const TAGS_NEGATIFS = [
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
];
const TAG_CONVERSATION = {
  label: 'Conversation',
  id: 'conversation',
  icon: 'speak-line',
};
const { subscribe } = derived([storeConversation], ([conversation]) => {
  if (
    conversation.messages.filter((m) => m.emetteur === 'utilisateur').length >= 2
  ) {
    return {
      positifs: () => [TAG_CONVERSATION, ...TAGS_POSITIFS],
      negatifs: () => [TAG_CONVERSATION, ...TAGS_NEGATIFS],
    };
  }
  return {
    positifs: () => TAGS_POSITIFS,
    negatifs: () => TAGS_NEGATIFS,
  };
});

export const storeTags = {
  subscribe,
};
