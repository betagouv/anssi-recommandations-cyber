<script lang="ts">
  import Conversation from "./lib/Conversation.svelte";
</script>

<main>
  <Conversation />
</main>

<style>
  :global(body) {
    background: #212121;
    color: white;
  }

  main {
    padding: var(--marge);
    padding-top: 120px;
    padding-bottom: 120px;
  }
</style>