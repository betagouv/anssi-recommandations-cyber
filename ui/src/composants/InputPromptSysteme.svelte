<script lang="ts">
  let { prompt = $bindable() }: { prompt: string } = $props();
</script>

<dsfr-textarea value={prompt} rows=10 onvaluechanged={(e: CustomEvent<string>) => prompt = e.detail}></dsfr-textarea>

<style>
  dsfr-textarea {
    margin-top: 24px;
  }
</style>
