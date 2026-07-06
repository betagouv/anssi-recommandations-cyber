<script lang="ts">
  import {
    type Completude,
    type Pertinence,
    storeAvisUtilisateurBis,
    type ValeurCompletude,
    type ValeurPertinence,
  } from '../stores/avisUtilisateurBis.store';
  import { clientAPI } from '../client.api';

  let afficheCommentairePertinence = $state(false);
  let afficheCommentaireCompletude = $state(false);
  let affichePrecisionPertinence = $state(false);
  let affichePrecisionEtSourcesCompletude = $state(false);
  let afficheMessageSucces = $state(false);
  let afficheMessageErreur = $state<string | undefined>(undefined);

  interface Props {
    idInteraction: string;
    idConversation: string;
  }

  const { idInteraction, idConversation }: Props = $props();

  $effect(() => {
    storeAvisUtilisateurBis.initialise({
      idConversation,
      idInteraction,
      pertinence: {} as Pertinence,
      completude: {} as Completude,
      estValide: false,
    });
  });

  type ValeurOptionPertinence =
    | 'tres-pertinente'
    | 'pertinente'
    | 'correcte'
    | 'erronee';
  type ValeurOptionCompletude = 'tres-bonne' | 'bonne' | 'correcte' | 'mauvaise';
  const mappeOptionsPertinenceValeurPertinence: Map<
    ValeurOptionPertinence,
    ValeurPertinence
  > = new Map([
    ['tres-pertinente', 'Très pertinente'],
    ['pertinente', 'Pertinente'],
    ['correcte', 'Correcte'],
    ['erronee', 'Erronée'],
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

  const surClickPertinence = (e: { detail: ValeurOptionPertinence }) => {
    afficheCommentairePertinence = e.detail !== 'erronee';
    affichePrecisionPertinence = e.detail === 'erronee';
    storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence(
      mappeOptionsPertinenceValeurPertinence.get(e.detail)!
    );
  };

  const surClickCompletude = (e: { detail: ValeurOptionCompletude }) => {
    afficheCommentaireCompletude = e.detail !== 'mauvaise';
    affichePrecisionEtSourcesCompletude = e.detail === 'mauvaise';
    storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude(
      mappeOptionsCempletudeValeurCompletude.get(e.detail)!
    );
  };

  const ajouteCommentairePertinence = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLaPertinence(e.detail);
  };

  const ajouteCommentaireCompletude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLaCompletude(e.detail);
  };

  const ajouteInformationsErronees = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.preciseLesInformationsErronees(e.detail);
  };

  const ajoutePrecisionsInformationsManquantesCompletude = (
    e: CustomEvent<string>
  ) => {
    storeAvisUtilisateurBis.preciseLesInformationsManquantes(e.detail);
  };

  const ajouteSourcesAdapteesCompletude = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(e.detail);
  };

  const soumetsAvisUtilisateur = async () => {
    try {
      await clientAPI.soumetsAvisUtilisateurBisAPI($storeAvisUtilisateurBis);
      afficheMessageSucces = true;
    } catch (erreur: unknown | Error) {
      afficheMessageErreur = (erreur as Error).message;
    }
  };
</script>

<div class="avis-utilisateur-bis">
  <div class="information-avis-utilisateur-bis">
    <span class="titre-avis"><b>Votre avis est essentiel ! 🙌</b></span>
    <span class="texte-avis"
      >En laissant votre avis, vous nous aidez à mieux comprendre vos besoins et à
      affiner nos réponses.</span
    >
  </div>
  {#if !afficheMessageSucces && !afficheMessageErreur}
    <div class="conteneur-avis-utilisateur-bis">
      <div class="avis-pertinence">
        <div class="avis-utilisateur-bis-options">
          <dsfr-radios-group
            radios={[
              {
                label: 'Très pertinente',
                id: 'tres-pertinente',
                name: 'options-pertinence',
                value: 'tres-pertinente',
              },
              {
                label: 'Pertinente',
                id: 'pertinente',
                name: 'options-pertinence',
                value: 'pertinente',
              },
              {
                label: 'Correcte',
                id: 'correcte',
                name: 'options-pertinence',
                value: 'correcte',
              },
              {
                label: 'Erronée',
                id: 'erronee',
                name: 'options-pertinence',
                value: 'erronee',
              },
            ]}
            legend="La réponse est-elle pertinente au regard de la question posée ?"
            legendSize="md"
            legendWeight="bold"
            size="md"
            status="default"
            error-message="Texte d’erreur"
            valid-message="Texte de succès"
            id="storybook-form"
            has-pictogram
            inline
            onvaluechanged={surClickPertinence}
          ></dsfr-radios-group>
        </div>
        {#if afficheCommentairePertinence}
          <div class="conteneur-commentaire">
            <dsfr-textarea
              label="Ajouter un commentaire"
              type="text"
              name="commentaire-pertinence"
              id="commentaire-pertinence"
              rows="3"
              maxlength="5000"
              onvaluechanged={ajouteCommentairePertinence}
            ></dsfr-textarea>
          </div>
        {/if}
        {#if affichePrecisionPertinence}
          <div class="info-champ-obligatoire">
            Les informations demandées sont obligatoires.
          </div>
          <div class="conteneur-commentaire">
            <dsfr-textarea
              label="Précisez les informations erronées (obligatoire)"
              type="text"
              name="informations-erronees"
              id="informations-erronees"
              rows="3"
              maxlength="5000"
              status={$storeAvisUtilisateurBis.pertinence.erreurs?.[
                'informations-erronees'
              ]
                ? 'error'
                : 'default'}
              error-message={$storeAvisUtilisateurBis.pertinence.erreurs?.[
                'informations-erronees'
              ] ?? ''}
              onvaluechanged={ajouteInformationsErronees}
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
          {#if afficheCommentaireCompletude}
            <div class="conteneur-commentaire">
              <dsfr-textarea
                label="Ajouter un commentaire"
                type="text"
                name="commentaire-completude"
                id="commentaire-completude"
                rows="3"
                maxlength="5000"
                onvaluechanged={ajouteCommentaireCompletude}
              ></dsfr-textarea>
            </div>
          {/if}
          {#if affichePrecisionEtSourcesCompletude}
            <div class="info-champ-obligatoire">
              Tous les Champs sont obligatoires
            </div>
            <div class="conteneur-commentaire">
              <dsfr-textarea
                label="Précisez les informations manquantes"
                type="text"
                name="precisions-completude"
                id="precisions-completude"
                rows="3"
                maxlength="5000"
                status={$storeAvisUtilisateurBis.completude.erreurs?.[
                  'informations-manquantes'
                ]
                  ? 'error'
                  : 'default'}
                error-message={$storeAvisUtilisateurBis.completude.erreurs?.[
                  'informations-manquantes'
                ] ?? ''}
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
                maxlength="5000"
                status={$storeAvisUtilisateurBis.completude.erreurs?.[
                  'sources-adaptees'
                ]
                  ? 'error'
                  : 'default'}
                error-message={$storeAvisUtilisateurBis.completude.erreurs?.[
                  'sources-adaptees'
                ] ?? ''}
                onvaluechanged={ajouteSourcesAdapteesCompletude}
              ></dsfr-textarea>
            </div>
          {/if}

          <div>
            <dsfr-button
              type="button"
              label="Envoyer vos commentaires"
              kind="primary"
              disabled={!$storeAvisUtilisateurBis.estValide}
              onclick={soumetsAvisUtilisateur}
            ></dsfr-button>
          </div>
        </div>
      </div>
    </div>
  {/if}
  {#if afficheMessageSucces}
    <div class="conteneur-message-retour-mqc">
      <dsfr-alert
        has-title={false}
        text="Merci ! Vos retours sont précieux. ✨"
        type="success"
        size="sm"
      ></dsfr-alert>
    </div>
  {/if}
  {#if afficheMessageErreur !== undefined && afficheMessageErreur !== '' && !afficheMessageSucces}
    <div class="conteneur-message-retour-mqc">
      <dsfr-alert
        has-title={false}
        text={afficheMessageErreur}
        type="warning"
        size="md"
      ></dsfr-alert>

      <dsfr-button
        type="button"
        label="Réessayer"
        kind="primary"
        onclick={soumetsAvisUtilisateur}
      ></dsfr-button>
    </div>
  {/if}
</div>

<style lang="scss">
  .avis-utilisateur-bis {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 24px;

    .conteneur-message-retour-mqc {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      align-self: stretch;
      gap: 16px;

      :first-child {
        min-width: stretch;
      }
    }
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
      font-size: 16px;
      line-height: 24px;
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
    background: #f9f6f2;

    .avis-pertinence,
    .avis-completude {
      display: flex;
      flex-direction: column;
      align-self: stretch;

      .conteneur-commentaire {
        min-width: stretch;
      }

      .info-champ-obligatoire {
        color: #0063cb;
        font-size: 14px;
        line-height: 24px;
        padding-bottom: 16px;
      }
    }
  }
</style>
