<script lang="ts">
  import InputPromptSysteme from "./InputPromptSysteme.svelte";
  import { storeAffichage } from "../stores/affichage.store";
  import { storeConversation } from "../stores/conversation.store";
  import { publieMessageUtilisateurAPI } from "../client.api";
  import { onMount, tick } from "svelte";

  let { urlAPI }: { urlAPI: string } = $props();

  let question: string = $state("");
  let promptSysteme: string = $state("");
  let afficheInputPromptSysteme = $state(false);
  let elementTextarea: HTMLTextAreaElement | undefined = $state();

  onMount(() => {
    recuperePromptSysteme();
    redimensionneZoneDeTexte();
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
    await tick();
    redimensionneZoneDeTexte();

    const { reponse, paragraphes, interaction_id } = await publieMessageUtilisateurAPI(message, afficheInputPromptSysteme);
    await storeConversation.ajouteMessageSysteme(reponse, paragraphes, interaction_id);

    storeAffichage.estEnAttenteDeReponse(false);
    await storeAffichage.scrollVersDernierMessage();
  }

  const KONAMI_CODE = [ "ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a", ];

  let combinaisonDeTouches: string[] = [];

  const touchePressee = (e: KeyboardEvent) => {
    const touche = e.key
    combinaisonDeTouches = (KONAMI_CODE[combinaisonDeTouches.length] === touche)
      ? combinaisonDeTouches.concat([touche])
      : [];

    const codeNulMaisFacile = e.ctrlKey && e.code === "Space";

    if (codeNulMaisFacile || KONAMI_CODE.length === combinaisonDeTouches.length) {
      afficheInputPromptSysteme = !afficheInputPromptSysteme;
    }
  }

  const redimensionneZoneDeTexte = () => {
    if(!elementTextarea) return;
    elementTextarea.style.height = 'auto';
    elementTextarea.style.height = `${Math.min(elementTextarea.scrollHeight, 96)}px`;
  }

  const gereTouchePresseeZoneDeTexte = (e: KeyboardEvent) => {
    if (e.code === "Enter" && !e.shiftKey) {
      soumetQuestion(e);
    }
  }
</script>

<svelte:body onkeydown={touchePressee} />
<form onsubmit={soumetQuestion} class="question-utilisateur">
  <span class="information-donnees-personnelles">Ne partagez aucune donnée personnelle ni information sensible sur votre organisation.</span>
  {#if afficheInputPromptSysteme}
    <InputPromptSysteme bind:prompt={promptSysteme} />
  {/if}
  <textarea
    placeholder="Posez votre question cyber"
    bind:value={question}
    bind:this={elementTextarea}
    oninput={redimensionneZoneDeTexte}
    onkeydown={gereTouchePresseeZoneDeTexte}
    rows="1"
  ></textarea>
  <button type="submit">
    <img src="./icons/fleche-envoi-message.svg" alt="" />
  </button>
</form>

<style lang="scss">
  .question-utilisateur {
    position: fixed;
    max-width: 840px;
    margin: 0 auto;
    width: calc(100% - 32px);
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 16px;
    border: 1px solid #DDDDDD;
    background: #F6F6F6;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 16px;
    padding: 12px;

    &:focus-within .information-donnees-personnelles {
      display: block;
    }

    .information-donnees-personnelles {
      color: #666666;
      text-align: center;
      font-size: 0.75rem;
      line-height: 1.25rem;
      width: 100%;
      position: absolute;
      top: -4px;
      transform: translateY(-100%);
      display: none;
    }

    textarea {
      width: 100%;
      box-sizing: border-box;
      text-overflow: ellipsis;
      font-family: Marianne;
      font-size: 1rem;
      line-height: 1.5rem;
      overflow: hidden;
      resize: none;
      border: none;
      background: none;

      &::placeholder {
        color: #666666;
      }
    }

    button {
      width: 40px;
      min-width: 40px;
      height: 40px;
      border-radius: 8px;
      background: #E5E5E5;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 24px;
      padding: 0;
      cursor: pointer;
    }
  }
</style>