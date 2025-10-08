<script lang="ts">
  import Entete from "./composants/Entete.svelte";
  import BandeauInformation from "./composants/BandeauInformation.svelte";
  import Conversation from "./composants/Conversation.svelte";
  import PromptUtilisateur from "./composants/PromptUtilisateur.svelte";

  let { urlAPI }: { urlAPI: string } = $props();
</script>

<Entete />
<main>
  <BandeauInformation />
  <Conversation />
  <PromptUtilisateur {urlAPI} />
</main>
