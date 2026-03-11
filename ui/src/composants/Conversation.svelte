<script lang="ts">
  import { fade } from 'svelte/transition';
  import BandeauAvisUtilisateur from './BandeauAvisUtilisateur.svelte';
  import {
    type Message,
    type MessageSysteme,
    type MessageUtilisateur,
    storeConversation,
  } from '../stores/conversation.store';
  import { onMount } from 'svelte';
  import { storeAffichage } from '../stores/affichage.store';
  import { infobulle } from '../directives/infobulle';
  import EcranErreur from './EcranErreur.svelte';
  import InputUtilisateur from './InputUtilisateur.svelte';
  import SourcesConversation from './SourcesConversation.svelte';

  let afficheBoutonScroll: boolean = $state(false);
  let { inputUtilisateur }: { inputUtilisateur: InputUtilisateur | undefined } =
    $props();

  const SEUIL_AFFICHAGE_BOUTON_SCROLL = 100;
  const gereScrollConversation = () => {
    const distanceFromBottom =
      document.documentElement.scrollHeight - (window.scrollY + window.innerHeight);
    afficheBoutonScroll = distanceFromBottom > SEUIL_AFFICHAGE_BOUTON_SCROLL;
  };

  onMount(() => {
    window.addEventListener('scroll', gereScrollConversation, { passive: true });
    gereScrollConversation();
    return () => window.removeEventListener('scroll', gereScrollConversation);
  });

  const copieLaReponse = (contenu: string) => {
    navigator.clipboard.writeText(contenu);
  };

  const estMessageSysteme = (
    message: Message | MessageSysteme | MessageUtilisateur
  ): message is MessageSysteme => message.emetteur === 'systeme';
</script>

<div class="conversation">
  {#each $storeConversation.messages as message, index (index)}
    {@const contenu = message.contenu}
    {@const contenuMarkdown = estMessageSysteme(message)
      ? message.contenuMarkdown
      : message.contenu}
    <div
      class="message"
      class:utilisateur={message.emetteur === 'utilisateur'}
      transition:fade
    >
      {#if message.emetteur === 'systeme'}
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        <p id={`reponse-mqc-${index}`}>{@html contenu}</p>
      {:else}
        <p>{message.contenu}</p>
      {/if}
    </div>
    {#if message.emetteur === 'systeme'}
      <div class="copie-reponse">
        <dsfr-button
          use:infobulle={{ contenu: 'Réponse copiée', mode: 'click' }}
          label="Copier la réponse"
          kind="tertiary-no-outline"
          size="md"
          id="copie-reponse"
          title="Copier la réponse"
          markup="button"
          type="button"
          onclick={() => copieLaReponse(contenuMarkdown)}
        ></dsfr-button>
      </div>
    {/if}
    <SourcesConversation {message} />
    {#if message.emetteur === 'systeme'}
      {@const idInteraction = message.idInteraction || ''}
      <BandeauAvisUtilisateur {idInteraction} />
    {/if}
  {/each}
  <div class="fondu-bas" class:visible={afficheBoutonScroll}></div>
  {#if $storeAffichage.enAttenteDeReponse}
    <div class="message utilisateur" transition:fade>
      <p>{$storeConversation.derniereQuestion}</p>
    </div>
    <div class="attente-reponse" in:fade>
      <img src="./icons/loader.svg" alt="" />
      <span>Un instant... Je parcours les guides de l’ANSSI.</span>
    </div>
  {/if}
  {#if $storeAffichage.aUneErreurAlbert && !$storeAffichage.enAttenteDeReponse}
    <EcranErreur
      message={$storeAffichage.messageErreurAlbert}
      onclick={() =>
        inputUtilisateur?.soumetLaQuestion($storeConversation.derniereQuestion)}
    />
  {/if}
  <div id="cible-scroll"></div>
</div>
{#if afficheBoutonScroll}
  <button
    class="bouton-scroll-rapide"
    onclick={storeAffichage.scrollVersDernierMessage}
  >
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
    margin: 0 auto 56px;

    #cible-scroll {
      scroll-margin-bottom: 120px;
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
      background-color: #eeeeee;
      align-self: flex-end;
      width: fit-content;
      max-width: 600px;
      box-sizing: border-box;
      overflow: hidden;
      text-overflow: ellipsis;
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
    background: #fff;
    cursor: pointer;
  }
</style>
