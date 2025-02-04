<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';
    import {tick} from "svelte";

    let demande: string = '';

    type Message = {
        contenu: string;
        documentsAssocies?: string[];
        expediteur: 'Moi' | 'Serveur';
        scoreMoyen?: number;
        chunks?: string[];
    }

    let messages: Message[] = [];
    let enAttente = false;
    const envoiDemande = async () => {
        enAttente = true;
        if (!demande) return;
        const contenu = (' ' + demande).slice(1);
        messages = [...messages, {contenu, expediteur: 'Moi'}];
        demande = '';

        const reponse = await (await fetch('/api/demande', {
            method: 'post',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({demande: contenu})
        })).json();

        const reponseAvecRecommandation = reponse.reponse.replaceAll(/(R\d+)/g, "**$1**");

        messages = [...messages, {
            contenu: reponseAvecRecommandation,
            documentsAssocies: reponse.sources,
            scoreMoyen: reponse.scoreMoyen,
            chunks: reponse.chunks,
            expediteur: 'Serveur'
        }];

        enAttente = false;
    };

    $: {
        if (messages.length) {
            tick().then(() => document.querySelector(".fin-conversation").scrollIntoView({behavior: "smooth"}));
        }
    }
</script>

<details>
    <summary>Ceci est une preuve de concept développée par l’équipe RecosCyber (Lab+BTI) à des fins de test strictement
        interne. Merci de ne pas communiquer l’URL à l’extérieur de l’Agence.
        <br><b>ℹ️ En savoir plus</b>
    </summary>
    <p>Ce POC a été développé par l’équipe RecosCyber en vue de tester l’utilisation de l’API Albert.</p>
    <p>L’objectif est de vérifier la faisabilité et l’opportunité de mettre à disposition des bénéficiaires de l’Agence
        (spécialistes ou non) un moteur de recherche capable de fournir des réponses en langage naturel et références
        précises, en réponse à leurs questions, à partir des publications de l’Agence et de ses partenaires.</p>
    <p>L’équipe RecoCyber travaille étroitement avec la DINUM (ETALAB / Alliance) en vue d’améliorer le fonctionnement
        de l’API Albert afin de permettre de réponses plus précises/fiables et la sécurité des données.</p>
    <p>Vous souhaitez contacter l’équipe RecoCyber ? Ecrivez à <a href="mailto:recosCyber@ssi.gouv.fr">recosCyber@ssi.gouv.fr</a></p>
</details>

<div class="conteneur-messages">
    {#each messages as message, idx (idx)}
        {@const estUtilisateur = message.expediteur === 'Moi'}
        <div class="message" class:estUtilisateur>
            {#if message.scoreMoyen}
                <span class="score">Score : {(message.scoreMoyen * 100).toFixed(1)}%</span>
            {/if}
            <p class="contenu-message">
                {#if message.chunks}
                    {#each message.chunks as chunk, index}
                        <p class="chunk">
                            <span>Chunk № {index + 1}</span>
                            <SvelteMarkdown source={chunk.replaceAll(/(R\d+)/g, "**$1**")}/>
                            <SvelteMarkdown source="___"/>
                        </p>
                    {/each}
                {/if}
                {#if message.expediteur === 'Serveur'}
                    <span>Réponse LLM :</span>
                {/if}
                <SvelteMarkdown source={message.contenu.replaceAll(/(R\d+)/g, "**$1**")}/>
                {#if message.documentsAssocies}
                    <div class="conteneur-source">
                        <span>Sources: </span>
                        {#each message.documentsAssocies as document}
                            <a href="/document/{document}">({document})</a>
                        {/each}
                    </div>
                {/if}
            </p>
            {#if message.expediteur === 'Serveur'}
                <p class="disclaimer-reponse"><i>Les réponses générées l’ont été en utilisant un modèle d’IA à des fins de test et n’engagent pas l’ANSSI.</i></p>
            {/if}
        </div>
    {/each}
    <p class="fin-conversation"></p>
</div>
{#if enAttente}
    <div class="conteneur-loader">
        <div class="loader"/>
    </div>
{/if}
<form on:submit|preventDefault={envoiDemande}>
    <input type="text" bind:value={demande} placeholder="Posez votre question !"/>
    <button type="submit"/>
</form>

<style>
    .conteneur-messages {
        display: flex;
        flex-direction: column;
        gap: 32px;
        margin-bottom: 32px;
    }

    .message {
        max-width: 828px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 13px 11px 13px 32px;
        border-left: 4px solid #6A6AF4;
        margin-left: 20px;
        position: relative;
        background: #303030;
        border-radius: 8px;
    }

    .message p {
        margin: 0;
    }

    .message.estUtilisateur {
        align-self: end;
        padding-left: 13px;
        border: none;
        margin-left: 0;
    }

    :global(.message.estUtilisateur .contenu-message p) {
        margin: 0;
    }

    input {
        border-radius: 8px;
        width: 100%;
        border: none;
        padding: 13px 18px;
        text-align: right;
        outline: none;
        background: #303030;
        color: white;
        font-family: "Marianne";
    }

    input:focus-visible {
        outline: solid #6A6AF4;
    }

    button {
        display: none;
    }

    form {
        display: flex;
        justify-content: end;
        position: fixed;
        width: calc(100% - 240px);
        left: 120px;
        bottom: 48px;
    }

    .conteneur-loader {
        display: flex;
        justify-content: right;
        margin-bottom: 24px;
    }

    .loader {
        width: 30px;
        aspect-ratio: 2;
        --_g: no-repeat radial-gradient(circle closest-side, #6A6AF4 90%, #0000);
        background: var(--_g) 0% 50%,
        var(--_g) 50% 50%,
        var(--_g) 100% 50%;
        background-size: calc(100% / 3) 50%;
        animation: l3 1s infinite linear;
    }

    @keyframes l3 {
        20% {
            background-position: 0% 0%, 50% 50%, 100% 50%
        }
        40% {
            background-position: 0% 100%, 50% 0%, 100% 50%
        }
        60% {
            background-position: 0% 50%, 50% 100%, 100% 0%
        }
        80% {
            background-position: 0% 50%, 50% 50%, 100% 100%
        }
    }

    .score {
        width: fit-content;
        font-size: 0.7rem;
        background: #6A6AF4;
        padding: 2px 4px;
        color: white;
        font-weight: bold;
        border-radius: 4px;
    }

    .fin-conversation {
        margin: 0;
        visibility: hidden;
        height: 0;
    }

    .conteneur-source {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .conteneur-source span {
        font-size: 0.8rem;
    }

    .conteneur-source a {
        font-size: 0.7rem;
        background: #6A6AF4;
        padding: 2px 4px;
        color: white;
        font-weight: bold;
        border-radius: 4px;
        max-width: 140px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
    }

    details {
        position: fixed;
        top: 0;
        left: 0;
        width: calc(100% - 240px);
        background: #212121;
        z-index: 1;
        padding: 16px 120px;
        border-bottom: 1px solid #6A6AF4;
        cursor: pointer;
    }

    summary {
        list-style: none;
    }

    summary::-webkit-details-marker {
        display: none;
    }

    a {
        color: #6A6AF4;
    }

    .disclaimer-reponse {
        font-size: 0.7rem;
    }

    .chunk {
        font-size: 0.8rem;
    }
</style>