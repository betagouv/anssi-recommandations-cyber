<script lang="ts">
  import { clic } from '../actions.svelte';

  let { onclick }: { onclick: () => Promise<void> | undefined } = $props();
</script>

<div class="conteneur-erreur">
  <dsfr-alert
    button-close-label={undefined}
    has-title={true}
    title="Oups, un problème est survenu."
    has-description={true}
    text="Nos équipes font le maximum pour rétablir le service au plus vite ! Vous pouvez réessayer de charger la réponse ou revenir plus tard si le problème persiste."
    type="error"
    size="md"
    dismissible={false}
  ></dsfr-alert>

  <dsfr-button
    label="Réessayer"
    kind={1}
    size="md"
    disabled={false}
    has-icon={true}
    icon="refresh-line"
    icon-place="left"
    markup="button"
    type="button"
    use:clic={onclick}
  ></dsfr-button>
</div>

<style lang="scss">
  .conteneur-erreur {
    display: flex;
    max-width: 49.5rem;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    align-self: stretch;
  }
</style>
