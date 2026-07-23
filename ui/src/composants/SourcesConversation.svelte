<script lang="ts">
  import type { Message } from '../stores/conversation.store';
  import { infobulle } from '../directives/infobulle';

  interface Props {
    message: Message;
  }

  const { message }: Props = $props();

  let sourceCourante = $state(0);
  let listeElement: HTMLDivElement | undefined = $state();

  const deplaceADroite = () => {
    if (listeElement) {
      sourceCourante += 1;
      const elementListe = listeElement.children.item(sourceCourante);
      elementListe?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      });
    }
  };

  const deplaceAGauche = () => {
    if (listeElement) {
      sourceCourante -= 1;
      const elementListe = listeElement.children.item(sourceCourante);
      elementListe?.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      });
    }
  };

  const copieLesSourcesDeLaReponse = (message: Message) => {
    navigator.clipboard.writeText(
      (
        message.references?.map(
          (reference) =>
            `${reference.nom_document}\n${window.location.origin}${reference.url}`
        ) || ['']
      ).join('\n\n')
    );
  };
</script>

{#if message.references && message.references.length > 0}
  <details class="conteneur-sources" open>
    <summary>
      Sources ({message.references.length})
      <img src="./icons/fleche-extension.svg" alt="" />
    </summary>

    <div class="sources">
      <div class="actions-sources">
        <div class="copie-sources">
          <dsfr-button
            use:infobulle={{ contenu: 'Sources copiées', mode: 'click' }}
            label="Copier les sources de la réponse"
            kind="secondary"
            size="sm"
            id="copie-sources"
            title="Copier les sources de la réponse"
            markup="button"
            type="button"
            onclick={() => copieLesSourcesDeLaReponse(message)}
            data-copie-sources="copie-sources"
          ></dsfr-button>
        </div>
        <div class="navigation-carrousel">
          {#if sourceCourante > 0}
            <dsfr-button
              label="< Précédent"
              kind="secondary"
              size="sm"
              onclick={deplaceAGauche}
            ></dsfr-button>
          {/if}
          <dsfr-button
            label="Suivant >"
            kind="secondary"
            size="sm"
            disabled={message.references === undefined ||
              sourceCourante === message.references.length - 1}
            onclick={deplaceADroite}
          ></dsfr-button>
        </div>
      </div>
      <div class="sources-liste" bind:this={listeElement}>
        {#each message.references as reference, index (index)}
          {@const titreDuLien =
            reference.numero_page > 0
              ? `Page ${reference.numero_page}`
              : 'En savoir plus'}
          {@const imageUrl = URL.createObjectURL(reference.image ?? new Blob())}
          <div class="source">
            <span class="nom-document"
              >{reference.titre || reference.nom_document}</span
            >
            {#if reference.date_mise_a_jour}
              <span class="date-mise-a-jour">
                Publié le {Intl.DateTimeFormat('fr-FR', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                }).format(reference.date_mise_a_jour)}
              </span>
            {:else}
              <span> &nbsp; </span>
            {/if}
            <dsfr-link
              label={titreDuLien}
              href={reference.url}
              blank
              title={reference.titre || reference.nom_document}
            ></dsfr-link>
            <div class="contenu-reference">
              <img src={imageUrl} alt="" />
            </div>
          </div>
        {/each}
      </div>
    </div>
  </details>
{/if}

<style lang="scss">
  .contenu-reference {
    white-space: pre-line;
    margin-top: 8px;
    background-color: white;
    padding: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    aspect-ratio: 841 / 1190;
    width: 300px;

    @media screen and (min-width: 767px) {
      width: 500px;
    }

    img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
  }

  .conteneur-sources {
    margin: 24px 0;
    width: 100vw;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    padding: 24px 24px 48px 24px;
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
      max-width: 1200px;

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
      max-width: 1200px;
    }

    .actions-sources {
      display: flex;
      justify-content: space-between;
    }

    .copie-sources {
      display: flex;
      justify-content: flex-start;
      gap: 8px;
      margin-bottom: 16px;
    }

    .navigation-carrousel {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      margin-bottom: 16px;
    }

    .sources-liste {
      display: flex;
      flex-direction: row;
      gap: 24px;
      overflow-x: auto;
      scroll-behavior: smooth;
      padding-bottom: 8px;

      &::-webkit-scrollbar {
        height: 8px;
      }

      &::-webkit-scrollbar-track {
        background: #f1f1f1;
      }

      &::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 4px;
      }
    }

    .source {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .date-mise-a-jour {
        font-size: 0.75rem;
        font-style: italic;
        color: #6b7280;
      }
      .nom-document {
        font-weight: bold;
        overflow-wrap: anywhere;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }
</style>
