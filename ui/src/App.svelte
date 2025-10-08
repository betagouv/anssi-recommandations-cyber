<script lang="ts">
  import { onMount } from "svelte";
  import InputPromptSysteme from "./composants/InputPromptSysteme.svelte";
  import Entete from "./composants/Entete.svelte";
  import BandeauInformation from "./composants/BandeauInformation.svelte";
  import { storeConversation } from "./stores/conversation.store";
  import { publieMessageUtilisateurAPI } from "./client.api";
  import Conversation from "./composants/Conversation.svelte";
  import { storeAffichage } from "./stores/affichage.store";

  let { urlAPI }: { urlAPI: string } = $props();

  let question: string = $state("");
  let promptSysteme: string = $state("");

  onMount(() => {
    recuperePromptSysteme();
  });

  async function recuperePromptSysteme() {
    const reponse = await fetch(`${urlAPI}/api/prompt`);
    promptSysteme = await reponse.json();
  }

  async function soumetQuestion(e: Event) {
    storeAffichage.estEnAttenteDeReponse(true);
    e.preventDefault();
    if(!question) return;

    storeConversation.ajouteMessageUtilisateur(question);
    await storeAffichage.scrollVersDernierMessage();

    const message = afficheInputPromptSysteme
          ? { question, prompt: promptSysteme }
          : { question };

    question = "";

    const { reponse, paragraphes, interaction_id } = await publieMessageUtilisateurAPI(message, afficheInputPromptSysteme);
    await storeConversation.ajouteMessageSysteme(reponse, paragraphes, interaction_id);

    storeAffichage.estEnAttenteDeReponse(false);
    await storeAffichage.scrollVersDernierMessage();
  }

  const KONAMI_CODE = [ "ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a", ];

  let combinaisonDeTouches: string[] = [];
  let afficheInputPromptSysteme = $state(false);

  const touchePressee = (e: KeyboardEvent) => {
    const touche = e.key
    combinaisonDeTouches = (KONAMI_CODE[combinaisonDeTouches.length] === touche)
      ? combinaisonDeTouches.concat([touche])
      : [];

    const codeNulMaisFacile = e.ctrlKey && e.code === "Space";

    if (codeNulMaisFacile || KONAMI_CODE.length === combinaisonDeTouches.length) {
      afficheInputPromptSysteme = true;
    }
  }
</script>

<svelte:body onkeydown={touchePressee} />
<Entete />
<main>
  <BandeauInformation />
  <Conversation />

  <form onsubmit={soumetQuestion} class="question-utilisateur">
    <input placeholder="Posez votre question cyber" bind:value={question} type="text" />
    <button type="submit">
      <img src="./icons/fleche-envoi-message.svg" alt="" />
    </button>
    {#if afficheInputPromptSysteme}
      <InputPromptSysteme bind:prompt={promptSysteme} />
    {/if}
  </form>
</main>

<style lang="scss">
  .question-utilisateur {
    padding: 0 16px 24px;
    position: fixed;
    max-width: 840px;
    margin: 0 auto;
    width: calc(100% - 32px);
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);

    input[type="text"] {
      padding: 12px;
      width: 100%;
      height: 64px;
      box-sizing: border-box;
      border-radius: 16px;
      border: 1px solid #DDDDDD;
      background: #F6F6F6;
      text-overflow: ellipsis;
      font-family: Marianne;
      font-size: 1rem;
      line-height: 1.5rem;

      &::placeholder {
        color: #666666;
      }
    }

    button {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      background: #E5E5E5;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 24px;
      padding: 0;
      position: absolute;
      top: 12px;
      right: 24px;
      cursor: pointer;
    }
  }

</style>
