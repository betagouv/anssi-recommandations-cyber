<script lang="ts">
  import Entete from "./composants/Entete.svelte";
  import BandeauInformation from "./composants/BandeauInformation.svelte";
  import Conversation from "./composants/Conversation.svelte";
  import Introduction from "./composants/Introduction.svelte";
  import InputUtilisateur from "./composants/InputUtilisateur.svelte";

  import { fade } from "svelte/transition";
  import { storeConversation } from "./stores/conversation.store";

  let { urlAPI }: { urlAPI: string } = $props();
</script>

<Entete />
<main>
  <BandeauInformation />
  {#if $storeConversation.length === 0}
    <div transition:fade><Introduction /></div>
  {:else}
    <div transition:fade><Conversation /></div>
  {/if}
  <InputUtilisateur {urlAPI} />
</main>
