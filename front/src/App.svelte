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
    padding: 120px;
  }
</style>