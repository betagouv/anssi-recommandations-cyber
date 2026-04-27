<script lang="ts">
  import { infobulle } from '../directives/infobulle';
  import {
    type AvisUtilisateur,
    storeAvisUtilisateur,
  } from '../stores/avisUtilisateur.store';
  import {
    soumetsAvisUtilisateurAPI,
    supprimeAvisUtilisateurAPI,
  } from '../client.api';
  import { SvelteSet } from 'svelte/reactivity';
  import { TAGS_NEGATIFS, TAGS_POSITIFS } from './tags';

  let { idInteraction }: { idInteraction: string } = $props();
  const avisUtilisateur: AvisUtilisateur | undefined = $derived.by(
    () => $storeAvisUtilisateur[idInteraction]
  );
  const titreBlocAvis: string = $derived.by(() =>
    avisUtilisateur?.positif
      ? 'Dites-nous ce que vous avez apprécié ✨'
      : 'Expliquez-nous ce qui peut être amélioré 🛠️'
  );
  let commentaire: string = $state('');
  let tagsSelectionnes: SvelteSet<string> = new SvelteSet<string>();

  const remiseAZero = () => {
    commentaire = '';
    tagsSelectionnes.clear();
  };

  const afficheAvisUtilisateur = async (positif: boolean) => {
    remiseAZero();
    if (
      !avisUtilisateur ||
      (avisUtilisateur && avisUtilisateur.positif !== positif)
    ) {
      storeAvisUtilisateur.ajouteAvis(idInteraction, { positif, soumis: false });
      await soumetsAvisUtilisateurAPI(idInteraction, positif);
    } else {
      await supprimeAvisUtilisateurAPI(idInteraction);
      storeAvisUtilisateur.supprimeAvis(idInteraction);
    }
  };

  const soumetsAvisUtilisateur = async (avecCommentaire: boolean) => {
    storeAvisUtilisateur.soumetsAvis(idInteraction);
    await soumetsAvisUtilisateurAPI(
      idInteraction,
      avisUtilisateur.positif,
      avecCommentaire ? commentaire : undefined,
      tagsSelectionnes.size > 0 ? [...tagsSelectionnes] : undefined
    );
    remiseAZero();
  };
  const onselected = (e: CustomEvent) => {
    tagsSelectionnes.add(e.detail);
  };
  const onunselected = (e: CustomEvent) => {
    tagsSelectionnes.delete(e.detail);
  };
  const onvaluechanged = (e: CustomEvent) => {
    commentaire = e.detail;
  };
</script>

<div class="avis-utilisateur">
  <div class="texte-information-avis-utilisateur">
    <span class="titre-avis"><b>Votre avis est essentiel ! 🙌</b></span>
    <span
      >En partageant votre avis, vous participez à améliorer les réponses pour
      l’ensemble des utilisateurs.</span
    >
  </div>
  <div class="conteneur-emoji-avis">
    <button
      use:infobulle={'Réponse utile'}
      onclick={() => afficheAvisUtilisateur(true)}
      class:actif={avisUtilisateur?.positif}
    >
      <img src="./icons/pouce-like.svg" alt="Réponse utile" />
    </button>
    <button
      use:infobulle={'Réponse inutile'}
      onclick={() => afficheAvisUtilisateur(false)}
      class:actif={avisUtilisateur && !avisUtilisateur.positif}
    >
      <img class="pas-utile" src="./icons/pouce-like.svg" alt="Réponse pas utile" />
    </button>
  </div>
  {#if avisUtilisateur && !avisUtilisateur.soumis}
    <div class="encart-commentaire-avis">
      <div>
        <span>Facultatif, mais super utile 😉 !</span>
        <span class="titre"><b>{titreBlocAvis}</b></span>
      </div>
      {#key avisUtilisateur}
        <dsfr-tags-group
          size="md"
          type="pressable"
          groupMarkup="ul"
          hasIcon={true}
          tags={avisUtilisateur.positif ? TAGS_POSITIFS : TAGS_NEGATIFS}
          {onselected}
          {onunselected}
        ></dsfr-tags-group>
      {/key}
      <dsfr-input
        label="Ajouter un commentaire"
        type="text"
        id={idInteraction}
        nom={`avis-${idInteraction}`}
        {onvaluechanged}
      ></dsfr-input>
      <div class="conteneur-bouton">
        <dsfr-button
          label="Envoyer vos commentaires"
          onclick={() => soumetsAvisUtilisateur(true)}
        ></dsfr-button>
        <dsfr-button
          label="Ne pas préciser"
          kind="tertiary"
          onclick={() => soumetsAvisUtilisateur(false)}
        ></dsfr-button>
      </div>
    </div>
  {:else if avisUtilisateur && avisUtilisateur.soumis}
    <dsfr-alert
      has-title={false}
      text="Merci ! Vos retours sont précieux. ✨"
      type="success"
      size="sm"
      dismissible
    ></dsfr-alert>
  {/if}
</div>

<style lang="scss">
  .avis-utilisateur {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .texte-information-avis-utilisateur {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .titre-avis {
        font-size: 1.125rem;
        line-height: 1.75rem;
      }
    }

    .conteneur-emoji-avis {
      display: flex;
      align-items: center;
      gap: 8px;

      button {
        width: 40px;
        height: 40px;
        padding: 8px;
        border: 1px solid #dddddd;
        background: none;
        cursor: pointer;

        &:hover {
          background: rgba(0, 0, 0, 0.04);
        }

        &.actif {
          background: #000091;

          img {
            filter: brightness(0) invert(1);
          }
        }
      }

      .pas-utile {
        transform: rotate(180deg);
      }
    }

    .encart-commentaire-avis {
      padding: 24px;
      background: #f9f6f2;
      display: flex;
      align-items: flex-start;
      flex-direction: column;
      gap: 16px;

      & > div {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .titre {
        font-size: 1.25rem;
        line-height: 1.75rem;
      }

      .conteneur-bouton {
        display: flex;
        flex-direction: column;
        gap: 16px;
        width: 100%;

        dsfr-button {
          width: 100%;
        }

        @media screen and (min-width: 768px) {
          flex-direction: row-reverse;

          dsfr-button {
            width: fit-content;
          }
        }
      }
    }

    dsfr-input {
      width: 100%;
    }
  }
</style>
