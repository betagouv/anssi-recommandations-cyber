<script lang="ts">
    let { chemin, classe } : { chemin: string; classe?: string } = $props();
</script>

<div style="mask: url({chemin}) no-repeat center; -webkit-mask: url({chemin}) no-repeat center;" class={classe}></div>

<style lang="scss">
  div {
    width: 24px;
    height: 24px;
    min-width: 24px;
    min-height: 24px;
    background-color: currentColor;
    mask-size: contain;
    -webkit-mask-size: contain;
  }
</style>