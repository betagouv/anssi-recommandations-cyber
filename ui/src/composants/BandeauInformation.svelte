<script lang="ts">
  let bandeauOuvert: boolean = $state(true);
  let bandeauBetaTestOuvert: boolean = $state(true);
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

{#if bandeauBetaTestOuvert}
<div class="bandeau-information">
    <div class="contenu-bandeau-information">
        <img src="./icons/information.svg" alt="" />
        <div><b>MesQuestionsCyber a pour but de vous fournir des réponses à des questions concernant la cybersécurité.</b> Le service prend aujourd'hui appui sur une base de connaissances composées de l'ensemble des guides et publications de l'ANSSI. MesQuestionsCyber est actuellement en phase d'expérimentation (Alpha) en vue d'améliorer la structuration de la base de connaissances et le "prompt system", à partir de vos retours.
            Ce que nous attendons de vous : poser un maximum de questions et pour chaque laisser un retour : 👍 ou 👎 , des tags et des commentaires. Merci pour votre participation !</div>
        <button onclick={() => bandeauBetaTestOuvert = false} aria-label="Fermeture du bandeau d'information">
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