<script lang="ts">
  import type { Message } from '../stores/conversation.store';

  interface Props {
    message: Message;
  }

  const { message }: Props = $props();
</script>

{#if message.references && message.references.length > 0}
  <details class="conteneur-sources" open>
    <summary>
      Sources
      <img src="./icons/fleche-extension.svg" alt="" />
    </summary>

    <div class="sources">
      {#each message.references as reference, index (index)}
        {@const titreDuLien =
          reference.numero_page > 0
            ? `Page ${reference.numero_page}`
            : 'En savoir plus'}
        {@const imageUrl = URL.createObjectURL(reference.image ?? new Blob())}
        <div class="source">
          <span class="nom-document">{reference.nom_document}</span>
          <dsfr-link
            label={titreDuLien}
            href={reference.url}
            blank
            title={reference.nom_document}
          ></dsfr-link>
          <div class="contenu-reference">
            <img src={imageUrl} alt="" />
          </div>
          {#if index !== message.references.length - 1}
            <hr />
          {/if}
        </div>
      {/each}
    </div>
  </details>
{/if}

<style lang="scss">
  .contenu-reference {
    white-space: pre-line;

    img {
      max-width: 75%;
      width: 75%;
      height: auto;
    }
  }

  .conteneur-sources {
    margin: 24px 0;
    width: 100vw;
    position: relative;
    left: 50%;
    transform: translateX(-50%);

    padding: 16px 0;
    background-color: #f6f6f6;

    summary,
    .sources {
      max-width: 840px;
      margin: 0 auto;
      padding-left: 16px;
      padding-right: 16px;
    }

    &[open] {
      summary {
        img {
          transform: rotate(180deg);
        }
      }
    }

    summary {
      font-size: 1.25rem;
      font-weight: bold;
      line-height: 1.75rem;
      user-select: none;
      cursor: pointer;
      position: relative;
      list-style: none;

      img {
        position: absolute;
        top: 1px;
        right: 16px;
        transition: transform 0.2s ease-in-out;
      }

      &::marker {
        content: '';
      }

      &::-webkit-details-marker {
        content: '';
        display: none !important;
        visibility: hidden;
      }
    }

    .sources {
      padding-top: 16px;
      padding-bottom: 32px;
      display: flex;
      flex-direction: column;
    }

    .source {
      display: flex;
      flex-direction: column;
      gap: 8px;

      .nom-document {
        font-weight: bold;
        overflow-wrap: anywhere;
      }

      hr {
        width: 100%;
        border: none;
        border-top: 1px solid #dddddd;
        margin: 16px 0;
      }
    }
  }
</style>
