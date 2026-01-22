<script>
</script>

<div class="bandeau">
    <div class="contenu-bandeau">
        <slot></slot>
    </div>
</div>

<style lang="scss">

  .bandeau {
    background-color: #E8EDFF;
    color: #0063CB;
    font-size: 1rem;
    line-height: 1.5rem;
    padding: 1rem 0 1.5rem;

    .contenu-bandeau {
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