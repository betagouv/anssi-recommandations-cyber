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
    idInteraction?: string;
  };
</script>

<script lang="ts">
  import { fade } from "svelte/transition";
  import { onMount, tick } from "svelte";
  import BandeauAvisUtilisateur from "./composants/BandeauAvisUtilisateur.svelte";
  import { writable } from "svelte/store";
  import IconeNonDSFR from "./composants/IconeNonDSFR.svelte";

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
      idInteraction: retourApplication.interaction_id,
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

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const darkModeStore = writable<boolean>(prefersDark);
  darkModeStore.subscribe((isDarkMode: boolean) => {
    document.documentElement.dataset.theme = isDarkMode ? "dark" : "light";
  })
</script>

<header>
  <h1>Mes Questions Cyber</h1>
  <label for="dark-mode">
    <input type="checkbox" id="dark-mode" bind:checked={$darkModeStore}/>
    <span>Dark mode</span>
  </label>
</header>

<main>
  {#if bandeauOuvert}
    <div class="bandeau-information">
      <div class="contenu-bandeau-information">
        <IconeNonDSFR chemin="./icons/information.svg" />
        <div><b>Les réponses, générées à l'aide de l'intelligence artificielle souveraine de la direction interministérielle du numérique (DINUM), sont indicatives et n'engagent pas l'ANSSI.</b> Pour des résultats plus précis, consultez les sources citées dans les réponses proposées.</div>
        <button onclick={fermeBandeauInformation} class="croix-fermeture">
          <lab-anssi-icone nom="close-line" taille="sm"></lab-anssi-icone>
        </button>
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
            <lab-anssi-icone nom="arrow-down-s-line" taille="md"></lab-anssi-icone>
          </summary>

          <div class="sources">
            {#each message.references as reference, index (index)}
              <div class="source">
                <span>{reference.nom_document}</span>
                <a href="{reference.url}#page={reference.numero_page}" target="_blank" rel="noopener">
                  Page {reference.numero_page}
                  <lab-anssi-icone nom="external-link-line" taille="sm"></lab-anssi-icone>
                </a>
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
    <button class="bouton-scroll-rapide" onclick={scrollVersDernierMessage} aria-label="Flêche de scroll rapide">
      <lab-anssi-icone nom="arrow-down-line" taille="sm"></lab-anssi-icone>
    </button>
  {/if}

  <form onsubmit={soumetQuestion} class="question-utilisateur">
    <input placeholder="Posez votre question cyber" bind:value={question} type="text" />
    <button type="submit">
      <lab-anssi-icone nom="arrow-right-line" taille="md"></lab-anssi-icone>
    </button>
  </form>
</main>

<style lang="scss">
  .bandeau-information {
    padding: 12px 16px;
    background-color: var(--fond-bandeau-info);
    color: var(--texte-bandeau-info);
    font-size: 1rem;
    line-height: 1.5rem;

    button {
      background: none;
      border: none;
      cursor: pointer;
      &:hover{
        background: none;
      }
      color: var(--texte-bandeau-info);
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
      background-color: var(--fond-contraste);
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
      background-color: var(--fond-grise);
      &[open] {
        summary {
          lab-anssi-icone {
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

        lab-anssi-icone {
          color: var(--texte);
          position: absolute;
          top: 1px;
          right: 0;
          transition: transform 0.2s ease-out;
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
          color: var(--texte-action);
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
          border-top: 1px solid var(--lisere-grise);
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
      border: 1px solid var(--lisere-grise);
      background: var(--fond-grise);
      text-overflow: ellipsis;
      font-family: Marianne;
      font-size: 1rem;
      line-height: 1.5rem;
      color: var(--texte);

      &::placeholder {
        color: var(--texte-grise);
      }
    }

    button {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      background: var(--fond-grise-sombre);
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
      color: var(--texte-grise-inverse);
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
    border: 1px solid var(--texte-action);
    background: var(--fond);
    color: var(--texte-action);
    cursor: pointer;
  }

  .fondu-bas {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    pointer-events: none;
    background: linear-gradient(to top, var(--fond), transparent);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .fondu-bas.visible {
    opacity: 1;
  }
</style>
