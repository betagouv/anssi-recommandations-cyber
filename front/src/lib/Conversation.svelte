<script lang="ts">
    import SvelteMarkdown from 'svelte-markdown';
    import {tick} from "svelte";

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

        const reponse = await fetch('/api/demande', {
            method: 'post',
            headers: {
                Accept: 'text/event-stream',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({demande: contenu})
        });

        if (!reponse.body) throw new Error("Erreur de lecture de body");

        let scoreMoyen = 0;
        let sources = [];
        for (let paire of reponse.headers.entries()) {
            if (paire[0] === 'x-score-moyen') {
                scoreMoyen = parseFloat(paire[1]);
            } else if (paire[0] === 'x-sources') {
                sources = JSON.parse(paire[1]);
            }
        }

        const lecteur = reponse.body.getReader();
        const decodeur = new TextDecoder();

        messages = [...messages, {
                contenu: "",
                documentsAssocies: sources,
                scoreMoyen,
                expediteur: 'Serveur'
            }];

        while (true) {
            const { value, done } = await lecteur.read();
            if (done) break;
            const chunk = decodeur.decode(value, { stream: true });
            let dernierMessage = messages[messages.length - 1];
            dernierMessage.contenu += chunk;
            messages = [...messages.slice(0, messages.length - 1), dernierMessage]
        }

        enAttente = false;
    };

    $: {
        if(messages.length) {
            tick().then(() => document.querySelector(".fin-conversation").scrollIntoView({behavior: "smooth"}));
        }
    }
</script>

<div class="conteneur-messages">
    {#each messages as message, idx (idx)}
        {@const estUtilisateur = message.expediteur === 'Moi'}
        <div class="message" class:estUtilisateur>
            {#if message.scoreMoyen}
                <span class="score">Score : {(message.scoreMoyen * 100).toFixed(1)}%</span>
            {/if}
            <p class="contenu-message">
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
</style>