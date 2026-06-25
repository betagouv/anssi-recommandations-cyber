<script lang="ts">
  import {
    type Completude,
    type Exactitude,
    storeAvisUtilisateurBis,
    type ValeurCompletude,
    type ValeurExactitude,
  } from '../stores/avisUtilisateurBis.store';

  let afficheCommentaireExactitude = $state(false);
  let afficheCommentaireCompletude = $state(false);
  let affichePrecisionEtSourcesExactitude = $state(false);
  let affichePrecisionEtSourcesCompletude = $state(false);

  interface Props {
    idInteraction: string;
    idConversation: string;
  }

  const { idInteraction, idConversation }: Props = $props();

  $effect(() => {
    storeAvisUtilisateurBis.initialise({
      idConversation,
      idInteraction,
      exactitude: {} as Exactitude,
      completude: {} as Completude,
      estValide: false,
    });
  });

  type ValeurOptionExactitude = 'tres-bonne' | 'bonne' | 'correcte' | 'fausse';
  type ValeurOptionCompletude = 'tres-bonne' | 'bonne' | 'correcte' | 'mauvaise';
  const mappeOptionsExactitudeValeurExactitude: Map<
    ValeurOptionExactitude,
    ValeurExactitude
  > = new Map([
    ['tres-bonne', 'Très bonne'],
    ['bonne', 'Bonne'],
    ['correcte', 'Correcte'],
    ['fausse', 'Fausse'],
  ]);
  const mappeOptionsCempletudeValeurCompletude: Map<
    ValeurOptionCompletude,
    ValeurCompletude
  > = new Map([
    ['tres-bonne', 'Très bonne'],
    ['bonne', 'Bonne'],
    ['correcte', 'Correcte'],
    ['mauvaise', 'Mauvaise'],
  ]);

  const surClickExactitude = (e: { detail: ValeurOptionExactitude }) => {
    afficheCommentaireExactitude = e.detail !== 'fausse';
    affichePrecisionEtSourcesExactitude = e.detail === 'fausse';
    storeAvisUtilisateurBis.modifieLaValeurDeLExactitude(
      mappeOptionsExactitudeValeurExactitude.get(e.detail)!
    );
  };

  const surClickCompletude = (e: { detail: ValeurOptionCompletude }) => {
    afficheCommentaireCompletude = e.detail !== 'mauvaise';
    affichePrecisionEtSourcesCompletude = e.detail === 'mauvaise';
    storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude(
      mappeOptionsCempletudeValeurCompletude.get(e.detail)!
    );
  };

  const ajouteCommentaireExactitude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLExactitude(e.detail);
  };

  const ajouteCommentaireCompletude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLaCompletude(e.detail);
  };

  const ajoutePrecisionsInformationsErroneesExactitude = (
    e: CustomEvent<string>
  ) => {
    storeAvisUtilisateurBis.preciseLesInformationsErronees(e.detail);
  };

  const ajoutePrecisionsInformationsManquantesCompletude = (
    e: CustomEvent<string>
  ) => {
    storeAvisUtilisateurBis.preciseLesInformationsManquantes(e.detail);
  };

  const ajouteSourcesAdapteesExactitude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(e.detail);
  };

  const ajouteSourcesAdapteesCompletude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(e.detail);
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
      disabled={!$storeAvisUtilisateurBis.estValide}
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
