<script lang="ts">
  import InputPromptSysteme from './InputPromptSysteme.svelte';
  import { storeAffichage } from '../stores/affichage.store';
  import { storeConversation } from '../stores/conversation.store';
  import { onMount, tick } from 'svelte';
  import { ValidateurQuestionUtilisateur } from './ValidateurQuestionUtilisateur';

  let { urlAPI }: { urlAPI: string } = $props();

  let question: string = $state('');
  let promptSysteme: string = $state('');
  let afficheInputPromptSysteme = $state(false);
  let elementTextarea: HTMLTextAreaElement | undefined = $state();
  let erreurValidation: string = $state('');
  const validateurQuestionUtilisateur = new ValidateurQuestionUtilisateur();

  onMount(() => {
    recuperePromptSysteme();
    redimensionneZoneDeTexte();
  });

  async function recuperePromptSysteme() {
    const reponse = await fetch(`${urlAPI}/api/prompt`);
    promptSysteme = await reponse.json();
  }

  export const soumetLaQuestion = async (questionASoumettre: string = question) => {
    storeConversation.questionEnAttenteDeReponse(questionASoumettre);
    await storeAffichage.scrollVersDernierMessage();

    question = '';
    await tick();
    redimensionneZoneDeTexte();

    await storeConversation.ajouteMessageUtilisateur({
      question: questionASoumettre,
      ...(afficheInputPromptSysteme &&
        promptSysteme !== '' && { prompt: promptSysteme }),
    });
    await storeAffichage.scrollVersDernierMessage();
  };

  const soumetQuestion = async (e: Event) => {
    e.preventDefault();
    if (validateurQuestionUtilisateur.estValide(question)) {
      erreurValidation = '';
      await soumetLaQuestion();
    } else {
      erreurValidation = validateurQuestionUtilisateur.valide(question);
    }
  };

  const KONAMI_CODE = [
    'ArrowUp',
    'ArrowUp',
    'ArrowDown',
    'ArrowDown',
    'ArrowLeft',
    'ArrowRight',
    'ArrowLeft',
    'ArrowRight',
    'b',
    'a',
  ];

  let combinaisonDeTouches: string[] = [];

  const touchePressee = (e: KeyboardEvent) => {
    const touche = e.key;
    combinaisonDeTouches =
      KONAMI_CODE[combinaisonDeTouches.length] === touche
        ? combinaisonDeTouches.concat([touche])
        : [];

    const codeNulMaisFacile = e.ctrlKey && e.code === 'Space';

    if (codeNulMaisFacile || KONAMI_CODE.length === combinaisonDeTouches.length) {
      afficheInputPromptSysteme = !afficheInputPromptSysteme;
    }
  };

  const redimensionneZoneDeTexte = () => {
    if (!elementTextarea) return;
    elementTextarea.style.height = 'auto';
    elementTextarea.style.height = `${Math.min(elementTextarea.scrollHeight, 96)}px`;
  };

  const gereChangementTexte = () => {
    redimensionneZoneDeTexte();
    if (validateurQuestionUtilisateur.estValide(question)) erreurValidation = '';
  };

  const gereTouchePresseeZoneDeTexte = (e: KeyboardEvent) => {
    if (e.code === 'Enter' && !e.shiftKey) {
      soumetQuestion(e);
    }
  };
</script>

<svelte:body onkeydown={touchePressee} />
<div class="conteneur-question-utilisateur">
  <form onsubmit={soumetQuestion} class="question-utilisateur">
    {#if afficheInputPromptSysteme}
      <InputPromptSysteme bind:prompt={promptSysteme} />
    {/if}
    <div class={erreurValidation === '' ? '' : 'question-erreur'}>
      <span class="information-donnees-personnelles"
        >Ne partagez aucune donnée personnelle ni information sensible sur votre
        organisation.</span
      >
      <textarea
        placeholder="Posez votre question cyber"
        bind:value={question}
        bind:this={elementTextarea}
        oninput={gereChangementTexte}
        onkeydown={gereTouchePresseeZoneDeTexte}
        rows="1"
        class:erreur={erreurValidation !== ''}
      ></textarea>
      <button
        type="submit"
        disabled={question === '' || erreurValidation !== ''}
        class:actif={question !== '' && erreurValidation === ''}
      >
        <img src="./icons/fleche-envoi-message.svg" alt="" />
      </button>
    </div>
    {#if erreurValidation}
      <div class="message-erreur">{erreurValidation}</div>
    {/if}
  </form>
</div>

<style lang="scss">
  .conteneur-question-utilisateur {
    display: flex;
    justify-content: stretch;
    justify-items: center;
  }

  .question-utilisateur {
    max-width: 840px;
    width: calc(100% - 32px);
    bottom: 24px;
    padding: 12px;
    box-sizing: border-box;
    margin: 0 16px;

    & > div {
      display: flex;
      flex-direction: row;
      align-items: center;
      gap: 16px;
    }

    @media screen and (min-width: 768px) {
      left: 50%;
      margin: 0 auto;
      width: 100%;
    }

    &:focus-within {
      outline: 2px solid #0a76f6;

      .information-donnees-personnelles {
        display: block;
      }
    }

    .information-donnees-personnelles {
      color: #666666;
      text-align: center;
      font-size: 0.75rem;
      line-height: 1.25rem;
      width: 100%;
      position: absolute;
      top: -2px;
      transform: translateY(-100%);
      display: none;
      left: 0;
      background: white;
    }

    .question-erreur::before {
      background-image: linear-gradient(0deg, #ce0500, #ce0500);
      content: '';
      display: block;
      pointer-events: none;
      position: absolute;
      top: 0;
      right: -0.75rem;
      bottom: 0;
      left: -0.75rem;
      background-repeat: no-repeat;
      background-position: 0 0;
      background-size: 0.125rem 100%;
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
      padding: 0.5rem 1rem;
      min-height: 28px;
      background-color: #eee;
      border-radius: 8px 8px 0 0;

      &::placeholder {
        color: #666666;
      }

      &:focus-visible {
        outline: none;
      }
    }

    textarea.erreur {
      box-shadow: inset 0 -2px 0 0 #ce0500;
    }

    button {
      width: 40px;
      min-width: 40px;
      height: 40px;
      border-radius: 8px;
      background: #e5e5e5;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 24px;
      padding: 0;
      cursor: pointer;

      &.actif {
        background: #000091;

        img {
          filter: brightness(0) invert(1);
        }
      }
    }
  }

  .message-erreur {
    color: #ce0500;
    font-size: 0.875rem;
    margin-top: 8px;
    text-align: center;
  }
</style>
