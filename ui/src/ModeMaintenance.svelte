<script lang="ts">
  import Entete from './composants/Entete.svelte';
  import PiedDePage from './composants/PiedDePage.svelte';
  import Bandeau from './composants/Bandeau.svelte';
</script>

<Entete />

<main>
  <Bandeau>
    <h2>MesQuestionsCyber est en maintenance</h2>
  </Bandeau>
  <dsfr-container>
    <div class="conteneur">
      <p>
        Le site est actuellement en maintenance pour des raisons techniques. Nous
        vous remercions de votre compréhension et de votre patience.
      </p>
    </div>
  </dsfr-container>
</main>

<PiedDePage />

<style lang="scss">
  .conteneur {
    padding: 2rem 0 3.5rem;
  }
</style>
