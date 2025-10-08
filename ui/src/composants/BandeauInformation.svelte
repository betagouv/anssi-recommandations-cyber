<script lang="ts">
  let bandeauOuvert: boolean = $state(true);
</script>

{#if bandeauOuvert}
  <div class="bandeau-information">
    <div class="contenu-bandeau-information">
      <img src="./icons/information.svg" alt="" />
      <div><b>Les réponses, générées à l'aide de l'intelligence artificielle souveraine de la direction interministérielle du numérique (DINUM), sont indicatives et n'engagent pas l'ANSSI.</b> Pour des résultats plus précis, consultez les sources citées dans les réponses proposées.</div>
      <button onclick={() => bandeauOuvert = false} aria-label="Fermeture du bandeau d'information">
        <lab-anssi-icone nom="close-line" taille="sm"></lab-anssi-icone>
      </button>
    </div>
  </div>
{/if}

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
      color: #0063CB;
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
</style>