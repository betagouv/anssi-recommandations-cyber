<script lang="ts">
  let afficheCommentaireExactitude = $state(false);
  let afficheCommentaireCompletude = $state(false);
  let affichePrecisionEtSourcesExactitude = $state(false);
  let affichePrecisionEtSourcesCompletude = $state(false);
  let envoiDesactive = $state(true);

  interface Props {
    idInteraction: string;
    idConversation: string;
  }

  const { idInteraction, idConversation }: Props = $props();

  type ValeurOptionExactitude = 'tres-bonne' | 'bonne' | 'correcte' | 'fausse';
  type ValeurOptionCompletude = 'tres-bonne' | 'bonne' | 'correcte' | 'mauvaise';

  const surClickExactitude = (e: { detail: ValeurOptionExactitude }) => {
    console.log('Exactitude', e.detail);
    console.log('IDs', { idInteraction, idConversation });
    afficheCommentaireExactitude = e.detail !== 'fausse';
    affichePrecisionEtSourcesExactitude = e.detail === 'fausse';
  };

  const surClickCompletude = (e: { detail: ValeurOptionCompletude }) => {
    console.log('Complétude', e.detail);
    afficheCommentaireCompletude = e.detail !== 'mauvaise';
    affichePrecisionEtSourcesCompletude = e.detail === 'mauvaise';
  };

  const ajouteCommentaireExactitude = (e: CustomEvent<string>) => {
    console.log('Commentaire exactitude', e.detail);
  };

  const ajouteCommentaireCompletude = (e: CustomEvent<string>) => {
    console.log('Commentaire complétude', e.detail);
  };

  const ajoutePrecisionsInformationsErroneesExactitude = (
    e: CustomEvent<string>
  ) => {
    console.log('Precisions erronées exactitude', e.detail);
  };

  const ajoutePrecisionsInformationsManquantesCompletude = (
    e: CustomEvent<string>
  ) => {
    console.log('Precisions manquantes complétude', e.detail);
  };

  const ajouteSourcesAdapteesExactitude = (e: CustomEvent<string>) => {
    console.log('Sources exactitude', e.detail);
  };

  const ajouteSourcesAdapteesCompletude = (e: CustomEvent<string>) => {
    console.log('Sources complétude', e.detail);
  };

  const soumetsAvisUtilisateur = async () => {};
</script>

<div class="avis-utilisateur-bis">
  <div class="information-avis-utilisateur-bis">
    <span class="titre-avis"><b>Votre avis est essentiel ! 🙌</b></span>
    <span class="texte-avis"
      >En laissant votre avis, vous nous aidez à mieux comprendre vos besoins et à
      affiner nos réponses.</span
    >
  </div>
  <div class="conteneur-avis-utilisateur-bis">
    <div class="avis-exactitude">
      <div class="avis-utilisateur-bis-options">
        <dsfr-radios-group
          radios={[
            {
              label: 'Très bonne',
              id: 'tres-bonne',
              name: 'options-exactitude',
              value: 'tres-bonne',
            },
            {
              label: 'Bonne',
              id: 'bonne',
              name: 'options-exactitude',
              value: 'bonne',
            },
            {
              label: 'Correcte',
              id: 'correcte',
              name: 'options-exactitude',
              value: 'correcte',
            },
            {
              label: 'Fausse',
              id: 'fausse',
              name: 'options-exactitude',
              value: 'fausse',
            },
          ]}
          legend="Exactitude de la réponse"
          size="md"
          status="default"
          error-message="Texte d’erreur"
          valid-message="Texte de succès"
          id="storybook-form"
          has-pictogram
          inline
          onvaluechanged={surClickExactitude}
        ></dsfr-radios-group>
      </div>
      {#if afficheCommentaireExactitude}
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Ajouter un commentaire"
            type="text"
            name="commentaire-exactitude"
            id="commentaire-exactitude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajouteCommentaireExactitude}
          ></dsfr-textarea>
        </div>
      {/if}
      {#if affichePrecisionEtSourcesExactitude}
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Précisez les informations erronées"
            type="text"
            name="precisions-exactitude"
            id="precisions-exactitude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajoutePrecisionsInformationsErroneesExactitude}
          ></dsfr-textarea>
        </div>
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Indiquez les sources adaptées (guide, page, paragraphes)"
            type="text"
            name="sources-adaptees-exactitude"
            id="sources-adaptees-exactitude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajouteSourcesAdapteesExactitude}
          ></dsfr-textarea>
        </div>
      {/if}
    </div>
    <div class="avis-completude">
      <div class="avis-utilisateur-bis-options">
        <dsfr-radios-group
          radios={[
            {
              label: 'Très bonne',
              id: 'tres-bonne',
              name: 'options-completude',
              value: 'tres-bonne',
            },
            {
              label: 'Bonne',
              id: 'bonne',
              name: 'options-completude',
              value: 'bonne',
            },
            {
              label: 'Correcte',
              id: 'correcte',
              name: 'options-completude',
              value: 'correcte',
            },
            {
              label: 'Mauvaise',
              id: 'mauvaise',
              name: 'options-completude',
              value: 'mauvaise',
            },
          ]}
          legend="Complétude de la réponse"
          size="md"
          status="default"
          error-message="Texte d’erreur"
          valid-message="Texte de succès"
          id="storybook-form"
          has-pictogram
          inline
          onvaluechanged={surClickCompletude}
        ></dsfr-radios-group>
      </div>
      {#if afficheCommentaireCompletude}
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Ajouter un commentaire"
            type="text"
            name="commentaire-completude"
            id="commentaire-completude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajouteCommentaireCompletude}
          ></dsfr-textarea>
        </div>
      {/if}
      {#if affichePrecisionEtSourcesCompletude}
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Précisez les informations manquantes"
            type="text"
            name="precisions-completude"
            id="precisions-completude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajoutePrecisionsInformationsManquantesCompletude}
          ></dsfr-textarea>
        </div>
        <div class="conteneur-commentaire">
          <dsfr-textarea
            label="Indiquez les sources adaptées (guide, page, paragraphes)"
            type="text"
            name="sources-adaptees-completude"
            id="sources-adaptees-completude"
            rows="3"
            maxlength="1000"
            onvaluechanged={ajouteSourcesAdapteesCompletude}
          ></dsfr-textarea>
        </div>
      {/if}
    </div>
  </div>
  <div>
    <dsfr-button
      type="button"
      label="Envoyer vos commentaires"
      kind="tertiary"
      {envoiDesactive}
      onclick={soumetsAvisUtilisateur}
    ></dsfr-button>
  </div>
</div>

<style lang="scss">
  .avis-utilisateur-bis {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 24px;
  }

  .information-avis-utilisateur-bis {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    align-self: stretch;

    .titre-avis {
      font-size: 18px;
      line-height: 28px;
    }

    .texte-avis {
      font-size: 14px;
      line-height: 20px;
    }
  }

  .conteneur-avis-utilisateur-bis {
    display: flex;
    padding: 24px;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 16px;
    align-self: stretch;

    .avis-exactitude,
    .avis-completude {
      display: flex;
      flex-direction: column;
      align-self: stretch;

      .conteneur-commentaire {
        min-width: stretch;
      }
    }
  }
</style>
