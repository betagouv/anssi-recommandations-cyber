<script lang="ts">
  import { storeAffichage } from "../stores/affichage.store";
  import { storeConversation } from "../stores/conversation.store";
  import { publieMessageUtilisateurAPI } from "../client.api";

  async function rempliQuestion(e: MouseEvent & { currentTarget: EventTarget & HTMLButtonElement }) {
    const suggestion: string = e.currentTarget.innerText;
    storeAffichage.estEnAttenteDeReponse(true);
    storeConversation.ajouteMessageUtilisateur(suggestion);
    await storeAffichage.scrollVersDernierMessage();

    const { reponse, paragraphes, interaction_id } = await publieMessageUtilisateurAPI({ question: suggestion }, false);
    await storeConversation.ajouteMessageSysteme(reponse, paragraphes, interaction_id);

    storeAffichage.estEnAttenteDeReponse(false);
    await storeAffichage.scrollVersDernierMessage();
  }
</script>

<div class="introduction">
  <p>MesQuestionsCyber a pour but de vous <b>fournir des réponses précises et sourcées aux questions de cybersécurité</b> à partir de <b>sources sélectionnées par l’ANSSI</b>.</p>
  <p>Pour cette version bêta, <b>la base de connaissance est uniquement basée sur les guides de l’ANSSI</b>. D'autres sources pourront venir enrichir la base de connaissance.</p>
  <p>Posez votre question ou choisissez parmi nos suggestions :</p>

  <ul>
    <li><button onclick={rempliQuestion}>Les réflexes à adopter en cas d’attaque par rançongiciel</button></li>
    <li><button onclick={rempliQuestion}>Organiser un exercice de gestion de crise cyber</button></li>
    <li><button onclick={rempliQuestion}>Réaliser une cartographie de mon SI</button></li>
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
        cursor: pointer;

        &:before {
          content: url("/icons/fleche-bas-scroll.svg");
          transform: rotate(-90deg);
          display: flex;
          width: 16px;
          height: 16px;
        }

        button {
          background: none;
          border: none;
          font-family: Marianne;
          font-size: 1rem;
          line-height: 1.5rem;
          text-decoration: underline;
          text-underline-offset: 5px;
          color: #000091;
          cursor: pointer;
          text-align: left;
        }
      }
    }
  }
</style>
