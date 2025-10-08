<script lang="ts">
  import { fade } from "svelte/transition";
  import { onMount, tick } from "svelte";
  import BandeauAvisUtilisateur from "./composants/BandeauAvisUtilisateur.svelte";
  import InputPromptSysteme from "./composants/InputPromptSysteme.svelte";
  import Entete from "./composants/Entete.svelte";
  import BandeauInformation from "./composants/BandeauInformation.svelte";
  import { storeConversation } from "./stores/conversation.store";

  let { urlAPI }: { urlAPI: string } = $props();

  let question: string = $state("");
  let enAttenteDeReponse: boolean = $state(false);
  let cibleScroll: HTMLDivElement | undefined = $state();
  let afficheBoutonScroll: boolean = $state(false);
  let promptSysteme: string = $state("");

  onMount(() => {
    window.addEventListener('scroll', gereScrollConversation, { passive: true });
    gereScrollConversation();
    recuperePromptSysteme();
    return () => window.removeEventListener('scroll', gereScrollConversation);
  });

  async function recuperePromptSysteme() {
    const reponse = await fetch(`${urlAPI}/api/prompt`);
    promptSysteme = await reponse.json();
  }

  async function soumetQuestion(e: Event) {
    enAttenteDeReponse = true;
    e.preventDefault();
    if(!question) return;

    storeConversation.ajouteMessageUtilisateur(question);
    await scrollVersDernierMessage();

    const endpoint = afficheInputPromptSysteme
      ? `${urlAPI}/api/pose_question_avec_prompt`
      : `${urlAPI}/api/pose_question`;

    const body = JSON.stringify(
        afficheInputPromptSysteme
          ? { question, prompt: promptSysteme }
          : { question }
    );

    question = "";

    const retourApplication = (await (await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    })).json());

    const { reponse, paragraphes, interaction_id } = retourApplication;
    await storeConversation.ajouteMessageSysteme(reponse, paragraphes, interaction_id);

    enAttenteDeReponse = false;
    await scrollVersDernierMessage();
  }

  const scrollVersDernierMessage = async() => {
    await tick();
    if(cibleScroll)
      cibleScroll.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  const SEUIL_AFFICHAGE_BOUTON_SCROLL = 100;
  const gereScrollConversation = () => {
    const distanceFromBottom = document.documentElement.scrollHeight - (window.scrollY + window.innerHeight);
    afficheBoutonScroll = distanceFromBottom > SEUIL_AFFICHAGE_BOUTON_SCROLL;
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
  <div class="conversation">
    {#each $storeConversation as message, index (index)}
      <div class="message" class:utilisateur={message.emetteur === "utilisateur"} transition:fade>
        {#if message.emetteur === "systeme"}
          <!-- eslint-disable-next-line svelte/no-at-html-tags -->
          <p>{@html message.contenu}</p>
        {:else}
          <p>{message.contenu}</p>
        {/if}
      </div>

      {#if message.references}
        <details class="conteneur-sources">
          <summary>
            Sources
            <img src="./icons/fleche-extension.svg" alt="" />
          </summary>

          <div class="sources">
            {#each message.references as reference, index (index)}
              <div class="source">
                <span>{reference.nom_document}</span>
                <a href="{reference.url}#page={reference.numero_page}" target="_blank" rel="noopener">Page {reference.numero_page} <img src="./icons/lien-externe.svg" alt="" /></a>
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
    {#if enAttenteDeReponse}
      <div class="attente-reponse" in:fade>
        <img src="./icons/loader.svg" alt="" />
        <span>Un instant... Je parcours les guides de l’ANSSI.</span>
      </div>
    {/if}
    <div id="cible-scroll" bind:this={cibleScroll}></div>
  </div>

  {#if afficheBoutonScroll}
    <button class="bouton-scroll-rapide" onclick={scrollVersDernierMessage}>
      <img src="./icons/fleche-bas-scroll.svg" alt="Flêche de scroll rapide" />
    </button>
  {/if}

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
  .conversation {
    display: flex;
    flex-direction: column;
    gap: 32px;
    padding: 32px 16px;
    font-size: 1rem;
    line-height: 1.5rem;
    max-width: 840px;
    margin: 0 auto 48px;

    #cible-scroll {
      scroll-margin-bottom: 120px;
    }

    .attente-reponse {
      display: flex;
      flex-direction: row;
      gap: 8px;
      img {
        animation: rotation 1s linear infinite;
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
          display: none;
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

        a {
          color: #000091;
          text-decoration: underline;
          text-decoration-thickness: 2px;
          text-underline-offset: 5px;
          display: flex;
          flex-direction: row;
          gap: 8px;
          align-items: baseline;

          img {
            width: 16px;
            height: 16px;
          }
        }

        span {
          font-weight: bold;
        }

        hr {
          width: 100%;
          border: none;
          border-top: 1px solid #DDDDDD;
          margin: 16px 0;
        }
      }
    }
  }

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

  .bouton-scroll-rapide {
    position: fixed;
    margin: 0 auto;
    bottom: 115px;
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

  .fondu-bas {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    pointer-events: none;
    background: linear-gradient(to top, rgba(255, 255, 255, 1), transparent);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .fondu-bas.visible {
    opacity: 1;
  }
</style>
