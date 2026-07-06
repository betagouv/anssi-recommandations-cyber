<script lang="ts">
  import {
    type SourcesAdaptees,
    type Pertinence,
    storeAvisUtilisateurBis,
    type ValeurSourcesAdaptees,
    type ValeurPertinence,
  } from '../stores/avisUtilisateurBis.store';
  import { clientAPI } from '../client.api';

  let afficheCommentairePertinence = $state(false);
  let afficheCommentaireSourcesAdaptees = $state(false);
  let affichePrecisionPertinence = $state(false);
  let affichePrecisionsSourcesAdaptees = $state(false);
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
      sourcesAdaptees: {} as SourcesAdaptees,
      estValide: false,
    });
  });

  type ValeurOptionPertinence =
    | 'tres-pertinente'
    | 'pertinente'
    | 'correcte'
    | 'erronee';
  type ValeurOptionSourcesAdaptees = 'oui-tout-a-fait' | 'oui-partiellement' | 'non';
  const mappeOptionsPertinenceValeurPertinence: Map<
    ValeurOptionPertinence,
    ValeurPertinence
  > = new Map([
    ['tres-pertinente', 'Très pertinente'],
    ['pertinente', 'Pertinente'],
    ['correcte', 'Correcte'],
    ['erronee', 'Erronée'],
  ]);

  const mappeOptionsSourcesAdapteesValeurSourcesAdaptees: Map<
    ValeurOptionSourcesAdaptees,
    ValeurSourcesAdaptees
  > = new Map([
    ['oui-tout-a-fait', 'Oui, tout à fait'],
    ['oui-partiellement', 'Oui, partiellement'],
    ['non', 'Non'],
  ]);

  const surClickPertinence = (e: { detail: ValeurOptionPertinence }) => {
    afficheCommentairePertinence = e.detail !== 'erronee';
    affichePrecisionPertinence = e.detail === 'erronee';
    storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence(
      mappeOptionsPertinenceValeurPertinence.get(e.detail)!
    );
  };

  const surClickSourcesAdaptees = (e: { detail: ValeurOptionSourcesAdaptees }) => {
    afficheCommentaireSourcesAdaptees = e.detail !== 'non';
    affichePrecisionsSourcesAdaptees = e.detail === 'non';
    storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
      mappeOptionsSourcesAdapteesValeurSourcesAdaptees.get(e.detail)!
    );
  };

  const ajouteCommentairePertinence = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLaPertinence(e.detail);
  };

  const ajouteCommentaireSourcesAdaptees = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.commenteLesSourcesAdaptees(e.detail);
  };

  const ajouteInformationsErronees = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.preciseLesInformationsErronees(e.detail);
  };

  const ajouteSourcesAdaptees = (e: CustomEvent<string>) => {
    storeAvisUtilisateurBis.indiqueLesSourcesAdaptees(e.detail);
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
            legend-size="md"
            legend-weight="bold"
            size="md"
            status="default"
            id="conteneur-options-pertinence"
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
      <div class="avis-sources-adaptees">
        <div class="avis-utilisateur-bis-options">
          <dsfr-radios-group
            radios={[
              {
                label: 'Oui, tout à fait',
                id: 'oui-tout-a-fait',
                name: 'options-sources-adaptees',
                value: 'oui-tout-a-fait',
              },
              {
                label: 'Oui, partiellement',
                id: 'oui-partiellement',
                name: 'options-sources-adaptees',
                value: 'oui-partiellement',
              },
              {
                label: 'Non',
                id: 'non',
                name: 'options-sources-adaptees',
                value: 'non',
              },
            ]}
            legend="Les sources citées sont-elles adaptées ?"
            size="md"
            status="default"
            legend-size="md"
            legend-weight="bold"
            id="conteneur-options-sources-adaptees"
            inline
            onvaluechanged={surClickSourcesAdaptees}
          ></dsfr-radios-group>
          {#if afficheCommentaireSourcesAdaptees}
            <div class="conteneur-commentaire">
              <dsfr-textarea
                label="Ajouter un commentaire"
                type="text"
                name="commentaire-sources-adaptees"
                id="commentaire-sources-adaptees"
                rows="3"
                maxlength="5000"
                onvaluechanged={ajouteCommentaireSourcesAdaptees}
              ></dsfr-textarea>
            </div>
          {/if}
          {#if affichePrecisionsSourcesAdaptees}
            <div class="info-champ-obligatoire">
              Les informations demandées sont obligatoires.
            </div>
            <div class="conteneur-commentaire">
              <dsfr-textarea
                label="Indiquez les sources adaptées"
                hint="Guides, numéro de page, paragraphes ..."
                type="text"
                name="sources-adaptees"
                id="sources-adaptees"
                rows="3"
                maxlength="5000"
                status={$storeAvisUtilisateurBis.sourcesAdaptees.erreurs?.[
                  'sources-adaptees'
                ]
                  ? 'error'
                  : 'default'}
                error-message={$storeAvisUtilisateurBis.sourcesAdaptees.erreurs?.[
                  'sources-adaptees'
                ] ?? ''}
                onvaluechanged={ajouteSourcesAdaptees}
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
    .avis-sources-adaptees {
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
