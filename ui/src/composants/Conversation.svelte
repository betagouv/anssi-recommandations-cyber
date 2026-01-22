<script lang="ts">
  import {fade} from "svelte/transition";
  import BandeauAvisUtilisateur from "./BandeauAvisUtilisateur.svelte";
  import {storeConversation} from "../stores/conversation.store";
  import {onMount} from "svelte";
  import {storeAffichage} from "../stores/affichage.store.js";
  import {infobulle} from "../directives/infobulle";

  let afficheBoutonScroll: boolean = $state(false);

  const SEUIL_AFFICHAGE_BOUTON_SCROLL = 100;
  const gereScrollConversation = () => {
    const distanceFromBottom = document.documentElement.scrollHeight - (window.scrollY + window.innerHeight);
    afficheBoutonScroll = distanceFromBottom > SEUIL_AFFICHAGE_BOUTON_SCROLL;
  }

  onMount(() => {
    window.addEventListener('scroll', gereScrollConversation, { passive: true });
    gereScrollConversation();
    return () => window.removeEventListener('scroll', gereScrollConversation);
  });

  const copieLaReponse = (contenu: string) => {
      navigator.clipboard.writeText(contenu);
  };
</script>


<div class="conversation">
  {#each $storeConversation as message, index (index)}
      {@const contenu = message.contenu}
    <div class="message" class:utilisateur={message.emetteur === "utilisateur"} transition:fade>

      {#if message.emetteur === "systeme"}
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          <p id={`reponse-mqc-${index}`}>{@html contenu}</p>
      {:else}
        <p>{message.contenu}</p>
      {/if}
    </div>
    {#if message.emetteur === "systeme"}
      <div class="copie-reponse">
        <dsfr-button
            use:infobulle={{contenu:"Réponse copiée", mode: 'click'}}
          label="Copier la réponse"
          kind="tertiary-no-outline"
          size="md"
          id="copie-reponse"
          title="Copier la réponse"
          markup="button"
          type="button"
          onclick={() => copieLaReponse(contenu)}
        ></dsfr-button>
      </div>
    {/if}
    {#if message.references && message.references.length > 0}
      <details class="conteneur-sources">
        <summary>
          Sources
          <img src="./icons/fleche-extension.svg" alt="" />
        </summary>

        <div class="sources">
          {#each message.references as reference, index (index)}
            <div class="source">
              <span class="nom-document">{reference.nom_document}</span>
              <dsfr-link
                label="Page {reference.numero_page}"
                href="{reference.url}#page={reference.numero_page}"
                blank
                title={reference.nom_document}
              />
              {#if index !== message.references.length - 1}
                <hr>
              {/if}
            </div>
          {/each}
        </div>
      </details>
    {/if}
    {#if message.emetteur === 'systeme'}
      {@const idInteraction = message.idInteraction || ''}
      <BandeauAvisUtilisateur {idInteraction} />
    {/if}
  {/each}
  <div class="fondu-bas" class:visible={afficheBoutonScroll}></div>
  {#if $storeAffichage.enAttenteDeReponse}
    <div class="attente-reponse" in:fade>
      <img src="./icons/loader.svg" alt="" />
      <span>Un instant... Je parcours les guides de l’ANSSI.</span>
    </div>
  {/if}
  <div id="cible-scroll"></div>
</div>
{#if afficheBoutonScroll}
  <button class="bouton-scroll-rapide" onclick={storeAffichage.scrollVersDernierMessage}>
    <img src="./icons/fleche-bas-scroll.svg" alt="Flêche de scroll rapide" />
  </button>
{/if}

<style lang="scss">
  .conversation {
    display: flex;
    flex-direction: column;
    gap: 32px;
    padding: 32px 16px;
    font-size: 1rem;
    line-height: 1.5rem;
    max-width: 840px;
    margin: 0 auto 120px;

    #cible-scroll {
      scroll-margin-bottom: 120px;
      display: none;
    }

    .attente-reponse {
      display: flex;
      flex-direction: row;
      gap: 8px;
      img {
        animation: rotation 1s linear infinite;
        width: 24px;
      }
    }

    @keyframes rotation {
      from {
        transform: rotate(0deg);
      }
      to {
        transform: rotate(360deg);
      }
    }

    .message.utilisateur {
      padding: 8px 16px;
      border-radius: 24px;
      background-color: #EEEEEE;
      align-self: flex-end;
      width: fit-content;
      max-width: 600px;
      box-sizing: border-box;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .conteneur-sources {
      margin: 24px 0;
      padding: 16px;
      background-color: #F6F6F6;
      &[open] {
        summary {
          img {
            transform: rotate(180deg);
          }
        }
      }

      summary {
        font-size: 1.25rem;
        font-weight: bold;
        line-height: 1.75rem;
        user-select: none;
        cursor: pointer;
        position: relative;
        list-style: none;

        img {
          position: absolute;
          top: 1px;
          right: 0;
          transition: transform 0.2s ease-in-out;
        }

        &::marker {
          content: "";
        }

        &::-webkit-details-marker {
          content: "";
          display: none !important;
          visibility: hidden;
        }
      }

      .sources {
        padding: 16px 32px 32px 32px;
        display: flex;
        flex-direction: column;
      }

      .source {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .nom-document {
          font-weight: bold;
          overflow-wrap: anywhere;
        }

        hr {
          width: 100%;
          border: none;
          border-top: 1px solid #DDDDDD;
          margin: 16px 0;
        }
      }
    }

    .fondu-bas {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 200px;
      pointer-events: none;
      background: linear-gradient(to top, white 0%, white 40%, transparent 100%);
      opacity: 0;
      transition: opacity 0.2s ease;
    }

    .fondu-bas.visible {
      opacity: 1;
    }
    .copie-reponse {
      display: flex;
      justify-content: flex-end;
    }
  }

  .bouton-scroll-rapide {
    position: fixed;
    margin: 0 auto;
    bottom: 120px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    padding: 8px;
    justify-content: center;
    align-items: center;
    border: 1px solid #000091;
    background: #FFF;
    cursor: pointer;
  }
</style>