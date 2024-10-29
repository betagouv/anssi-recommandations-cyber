<script lang="ts">
    import iconeFleche from '../assets/fleche_haut.svg';
    let demande: string = 'Comment stocker des mots de passes ?';

    type Message = {
        paragraphes: {
            contenu: string;
            documentAssocie?: string[];
        }[]
        expediteur: 'Moi' | 'Serveur';
    }

    let messages: Message[] = [];
    const envoiDemande = async () => {
        if (!demande) return;
        messages = [...messages, {paragraphes: [{contenu: demande}], expediteur: 'Moi'} ];
        const reponse = await (await fetch('/api/demande', {
            method: 'post',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ demande })
        })).json();


        messages = [...messages, {paragraphes: reponse.map(r => ({contenu: r.contenu, documentAssocie: r.document})), expediteur: 'Serveur'}];
        demande = '';
    };
</script>

<div class="conteneur-messages">
    {#each messages as message, idx (idx)}
        {@const estUtilisateur = message.expediteur === 'Moi'}
        <div class="message" class:estUtilisateur>
            {#each message.paragraphes as bloc}
                {@const document = bloc.documentAssocie}
                <p>
                    <span>{bloc.contenu}</span>
                    {#if document}
                        <a href="/document/{document}">({document})</a>
                    {/if}
                </p>
            {/each}
        </div>
    {/each}
</div>
<form on:submit|preventDefault={envoiDemande}>
    <input type="text" bind:value={demande} placeholder="Posez votre question !"/>
    <button type="submit" />
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
</style>