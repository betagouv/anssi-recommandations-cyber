<script context="module" lang="ts">
  type Paragraphe = {
    score_similarite: number,
    numero_page: number,
    url: string,
    nom_document: string,
    contenu: string,
  };

  type Message = {
    contenu: string;
    emetteur: "utilisateur" | "systeme";
    references?: Paragraphe[];
  };
</script>

<script lang="ts">
  import { fade } from "svelte/transition";
  import {onMount, tick} from "svelte";

  let { urlAPI }: { urlAPI: string } = $props();
  let bandeauOuvert: boolean = $state(true);
  let messages: Message[] = $state([]);
  let question: string = $state("");
  let enAttenteDeReponse: boolean = $state(false);
  let cibleScroll: HTMLDivElement | undefined = $state();
  let afficheBoutonScroll: boolean = $state(false);

  onMount(() => {
    window.addEventListener('scroll', gereScrollConversation, { passive: true });
    gereScrollConversation();
    return () => window.removeEventListener('scroll', gereScrollConversation);
  });

  async function soumetQuestion(e: Event) {
    enAttenteDeReponse = true;
    e.preventDefault();
    if(!question) return;

    messages = [...messages, {
      contenu: question,
      emetteur: "utilisateur",
    }];
    await scrollVersDernierMessage();

    const endpoint = `${urlAPI}/api/pose_question`;
    const body = JSON.stringify({ question });

    question = "";

    const retourApplication = (await (await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    })).json());

    messages = [...messages, {
      contenu: retourApplication.reponse,
      emetteur: "systeme",
      references: retourApplication.paragraphes,
    }];
    enAttenteDeReponse = false;
    await scrollVersDernierMessage();
  }

  const fermeBandeauInformation = () => {
    bandeauOuvert = false;
  };

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
</script>

<header>
  <h1>Mes Questions Cyber</h1>
</header>

<main>
  {#if bandeauOuvert}
    <div class="bandeau-information">
      <div class="contenu-bandeau-information">
        <img src="./icons/information.svg" alt="" />
        <div><b>Les réponses, générées à l'aide de l'intelligence artificielle souveraine de la direction interministérielle du numérique (DINUM), sont indicatives et n'engagent pas l'ANSSI.</b> Pour des résultats plus précis, consultez les sources citées dans les réponses proposées.</div>
        <button onclick={fermeBandeauInformation}><img src="./icons/croix-fermeture.svg" alt="Fermeture du bandeau informatif"/></button>
      </div>
    </div>
  {/if}

  <div class="conversation">
    {#each messages as message, index (index)}
      <div class="message" class:utilisateur={message.emetteur === "utilisateur"} transition:fade>
        <p>{message.contenu}</p>
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
                <a href="{reference.url}">Page {reference.numero_page} <img src="./icons/lien-externe.svg" alt="" /></a>
                {#if index !== message.references.length - 1}
                  <hr>
                {/if}
              </div>
            {/each}
          </div>
        </details>
      {/if}
    {/each}
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
  </form>
</main>

<style lang="scss">
  .bandeau-information {
    padding: 12px 16px;
    background-color: #E8EDFF;
    color: #0063CB;
    font-size: 1rem;
    line-height: 1.5rem;

    button {
      background: none;
      border: none;
      cursor: pointer;
      &:hover{
        background: none;
      }
    }

    .contenu-bandeau-information {
      display: flex;
      flex-direction: row;
      gap: 8px;
      align-items: flex-start;
      max-width: 1200px;
      box-sizing: border-box;
      margin: 0 auto;
    }
  }

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
</style>
