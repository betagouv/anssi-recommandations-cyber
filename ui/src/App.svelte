<script lang="ts">
  import Entete from './composants/Entete.svelte';
  import BandeauInformation from './composants/BandeauInformation.svelte';
  import Conversation from './composants/Conversation.svelte';
  import Introduction from './composants/Introduction.svelte';
  import InputUtilisateur from './composants/InputUtilisateur.svelte';

  import { fade } from 'svelte/transition';
  import { storeConversation } from './stores/conversation.store';
  import PiedDePage from './composants/PiedDePage.svelte';
  import { storeAffichage } from './stores/affichage.store';
  import BandeauInformationANSSI from './composants/BandeauInformationANSSI.svelte';
  import IntroductionANSSI from './composants/IntroductionANSSI.svelte';

  let inputUtilisateur: InputUtilisateur | undefined = $state(undefined);
  const estPublicInterneAnssi = () =>
    import.meta.env.VITE_PUBLIC_INTERNE_ANSSI === 'true';
</script>

<Entete />

<main class="main">
  <div class="bandeau">
    {#if estPublicInterneAnssi()}
      <BandeauInformationANSSI />
    {:else}
      <BandeauInformation />
    {/if}
  </div>

  <div class="contenu">
    {#if $storeConversation?.messages.length === 0 && !$storeAffichage.enAttenteDeReponse}
      <div transition:fade>
        {#if estPublicInterneAnssi()}
          <IntroductionANSSI />
        {:else}
          <Introduction />
        {/if}
      </div>
    {:else}
      <div transition:fade>
        <Conversation {inputUtilisateur} />
      </div>
    {/if}
  </div>

  <div class="question-utilisateur">
    <InputUtilisateur bind:this={inputUtilisateur} />
  </div>
</main>

<PiedDePage />

<style lang="scss">
  :global(html, body) {
    height: 100%;
  }

  :global(body) {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .bandeau {
    flex: 0 0 auto;
    min-height: 0;
  }

  .contenu {
    flex: 1;
    min-height: 0;
    overflow: auto;
  }

  .question-utilisateur {
    position: sticky;
    bottom: 0;
    flex: 0 0 auto;
    background: white; /* évite transparence au-dessus du contenu qui scroll */
    z-index: 10;
  }
</style>
