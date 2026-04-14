<script lang="ts">
  import { storeAffichage } from '../stores/affichage.store';
  import { storeConversation } from '../stores/conversation.store';

  const rempliQuestion = async (
    e: MouseEvent & { currentTarget: EventTarget & { label: string } }
  ) => {
    e.preventDefault();
    const suggestion: string = e.currentTarget.label;
    storeAffichage.estEnAttenteDeReponse(true);
    await storeAffichage.scrollVersDernierMessage();
    await storeConversation.ajouteMessageUtilisateur({ question: suggestion });
    await storeAffichage.scrollVersDernierMessage();
  };
</script>

<div class="introduction">
  <p>
    MesQuestionsCyber est destiné aux professionnels souhaitant des réponses <b
      >précises et sourcées à leurs questions de cybersécurité</b
    >.
  </p>
  <p>
    MesQuestionsCyber s’appuie sur <b
      >les guides et d’autres ressources de l’ANSSI
    </b> ainsi que d’autres sources de confiance comme des publications de la CNIL.
  </p>
  <p>Posez votre question ou choisissez parmi nos suggestions :</p>

  <ul>
    <li>
      <dsfr-link
        label="Quels sont les réflexes à adopter en cas d’attaque par rançongiciel en tant que PME française ?"
        href="#"
        onclick={rempliQuestion}
      ></dsfr-link>
    </li>
    <li>
      <dsfr-link
        label="Quel est l'intérêt d'organiser un exercice de gestion de crise cyber pour une PME ?"
        href="#"
        onclick={rempliQuestion}
      ></dsfr-link>
    </li>
    <li>
      <dsfr-link
        label="Pourquoi réaliser une cartographie de mon SI ?"
        href="#"
        onclick={rempliQuestion}
      ></dsfr-link>
    </li>
  </ul>
</div>

<style lang="scss">
  .introduction {
    box-sizing: border-box;
    max-width: 840px;
    padding: 32px 16px;
    margin: 0 auto 72px;
    display: flex;
    flex-direction: column;
    gap: 16px;

    @media screen and (min-width: 768px) {
      margin-top: 72px;
    }

    ul {
      list-style-type: none;
      padding-left: 0;
      display: flex;
      flex-direction: column;
      gap: 8px;

      li {
        display: flex;
        flex-direction: row;
        gap: 8px;
        align-items: center;

        &:before {
          content: url('/icons/fleche-bas-scroll.svg');
          transform: rotate(-90deg);
          display: flex;
          width: 16px;
          height: 16px;
        }
      }
    }
  }
</style>
