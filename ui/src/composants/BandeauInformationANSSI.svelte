<script lang="ts">
  let bandeauOuvert: boolean = $state(true);
</script>

{#if bandeauOuvert}
  <div class="bandeau-information">
    <div class="contenu-bandeau-information">
      <img src="./icons/information.svg" alt="" />
      <div>
        MesQuestionsCyber est un service permettant de poser des questions en matière
        de cybersécurité et d’obtenir des réponses en langage naturel, à l'appui des
        guides et ressources de l’ANSSI, ainsi que sur certaines publications de la
        CNIL.
      </div>
      <button
        onclick={() => (bandeauOuvert = false)}
        aria-label="Fermeture du bandeau d'information"
      >
        <lab-anssi-icone nom="close-line" taille="sm"></lab-anssi-icone>
      </button>
    </div>
  </div>
{/if}

<style lang="scss">
  .bandeau-information {
    padding: 12px 16px;
    background-color: #e8edff;
    color: #0063cb;
    font-size: 1rem;
    line-height: 1.5rem;

    button {
      background: none;
      border: none;
      cursor: pointer;
      color: #0063cb;

      &:hover {
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
</style>
