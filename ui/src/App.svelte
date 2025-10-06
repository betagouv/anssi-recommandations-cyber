<script lang="ts">
  let {url_api}: {url_api: string} = $props();

  type Paragraphe = {
    score_similarite: number,
    numero_page: number,
    url: string,
    nom_document: string,
    contenu: string,
  };

  let reponse: string;
  let references: Paragraphe[];

  async function soumetQuestion(e: Event) {
    e.preventDefault();
    const question = ((e!.target as HTMLFormElement)!.elements[0] as HTMLInputElement)!.value;

    const endpoint = `${url_api}/api/pose_question`;

    const retour_application = (await (await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    })).json());

    reponse = retour_application.reponse;
    references = retour_application.paragraphes;
  }

  let bandeauOuvert = $state(true);

  function fermeBandeauInformation() {
    bandeauOuvert = false;
  }
</script>

<header>
  <h1>Mes Questions Cyber</h1>
</header>

<main>
  {#if bandeauOuvert}
    <div class="bandeau-information">
      <div class="contenu-bandeau-information">
        <img src="./icons/information.svg" alt="" />
        <div><b>Les réponses, générées à l'aide de l'intelligence artificielle souveraine de la direction interministérielle du numérique (DINUM), sont indicatives et n'engagent pas l'ANSSI.</b> Pour des résultats plus précis, consultez les sources citées dans les réponses proposées.</div>
        <button onclick={fermeBandeauInformation}><img src="./icons/croix-fermeture.svg" alt="Fermeture du bandeau informatif"/></button>
      </div>
    </div>
  {/if}

  <div>{reponse}</div>

  <ul>{#each references as reference (`${reference.url}${reference.contenu}`)}
    <li>
      <a href="{reference.url}">{reference.nom_document}, p.{reference.numero_page}</a>
    </li>
  {/each}</ul>

  <form onsubmit={soumetQuestion}>
    <input placeholder="Posez votre question cyber"/>
    <input type="submit">
  </form>
</main>

<style lang="scss">
  .bandeau-information {
    padding: 12px 16px;
    background-color: #E8EDFF;
    color: #0063CB;
    font-size: 1rem;
    line-height: 1.5rem;

    button {
      background: none;
      border: none;
      cursor: pointer;
      &:hover{
        background: none;
      }
    }

    .contenu-bandeau-information {
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
