
describe('le store de conversation', () => {

  afterEach(() => {
    storeAvisUtilisateurBis.initialise({
      exactitude: {valeur: 'Bonne', commentaire: undefined},
      completude: {valeur: 'Bonne', commentaire: undefined},
      idConversation: '123',
      idInteraction: '456',
    });
  });

  it('modifie la valeur de l\'exactitude', () => {

      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Très bonne');
      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
      exactitude: {valeur: 'Très bonne', commentaire: undefined},
      completude: {valeur: 'Bonne', commentaire: undefined},
      idConversation: '123',
      idInteraction: '456',
    })

    });
});