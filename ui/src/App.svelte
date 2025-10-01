<script lang="ts">
  export let url_api: string;

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
</script>

<main>
  <div>Mes Questions Cyber</div>

  <div>{reponse}</div>

  <ul>{#each references as reference (`${reference.url}${reference.contenu}`)}
    <li>
      <a href="{reference.url}">{reference.nom_document}, p.{reference.numero_page}</a>
    </li>
  {/each}</ul>

  <form on:submit|preventDefault={soumetQuestion}>
    <input placeholder="Posez votre question cyber"/>
    <input type="submit">
  </form>
</main>

<style>
</style>
