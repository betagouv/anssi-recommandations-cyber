<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';

    let demande: string = '';

    type Message = {
        contenu: string;
        documentsAssocies?: string[];
        expediteur: 'Moi' | 'Serveur';
        scoreMoyen?: number;
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
            expediteur: 'Serveur'
        }];
        enAttente = false;
    };
</script>

<div class="conteneur-messages">
    {#each messages as message, idx (idx)}
        {@const estUtilisateur = message.expediteur === 'Moi'}
        <div class="message" class:estUtilisateur>
            {#if message.scoreMoyen}
                <span class="score">Score : {(message.scoreMoyen * 100).toFixed(1)}%</span>
            {/if}
            <p>
                <SvelteMarkdown source={message.contenu}/>
                {#if message.documentsAssocies}
                    {#each message.documentsAssocies as document}
                        <a href="/document/{document}">({document})</a>
                    {/each}
                {/if}
            </p>
        </div>
    {/each}
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
    }

    .message p {
        margin: 0;
    }

    .message.estUtilisateur {
        border-radius: 8px;
        align-self: end;
        background: #F1F1F1;
        padding-left: 13px;
        border: none;
        margin-left: 0;
    }

    input {
        border-radius: 8px;
        background: #F1F1F1;
        width: 100%;
        max-width: 660px;
        border: none;
        padding: 13px 18px;
        text-align: right;
        outline: none;
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
        position: absolute;
        top: 0;
        left: 32px;
        font-size: 0.7rem;
        background: #6A6AF4;
        padding: 2px 4px;
        color: white;
        font-weight: bold;
        border-radius: 4px;
    }
</style>