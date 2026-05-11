<script lang="ts">
  import Entete from './composants/Entete.svelte';
  import PiedDePage from './composants/PiedDePage.svelte';
  import Bandeau from './composants/Bandeau.svelte';

  const maintenance: { titre: string; contenu: string } = JSON.parse(
    import.meta.env.VITE_MAINTENANCE_MQC
  );
</script>

<Entete />

<main>
  <Bandeau>
    <h2>MesQuestionsCyber - {maintenance.titre}</h2>
  </Bandeau>
  <dsfr-container>
    <div class="conteneur">
      <p>
        {maintenance.contenu}
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
