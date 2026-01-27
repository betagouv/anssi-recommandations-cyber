<script lang="ts">
  import Entete from './composants/Entete.svelte';
  import Bandeau from './composants/Bandeau.svelte';
  import PiedDePage from './composants/PiedDePage.svelte';
</script>

<Entete />

<main class="container">
  <Bandeau>
    <h2>Mention d’information – MesQuestionsCyber</h2>
  </Bandeau>

  <dsfr-container>
    <div class="conteneur">
      <h2>Qui sommes-nous ?</h2>
      <p>
        La présente application est développée par l’Agence nationale de la sécurité
        des systèmes d'information, nommée ANSSI.
      </p>

      <h2>Interaction avec une intelligence artificielle</h2>
      <p>
        MesQuestionsCber est un système d’intelligence artificielle (chatbot) avec
        lequel vous interagissez dans les conditions prévues par les conditions
        générales d’utilisation. L’ANSSI ne traite pas de données à caractère
        personnel dans le cadre de MesQuestionsCyber. Nous vous rappelons que la
        confidentialité de vos informations est essentielle et son respect intervient
        dans le respect des conditions générales d’utilisation de MesQuestionsCyber.
      </p>

      <h2>Utilisons-nous vos données personnelles ?</h2>
      <p>
        L’ANSSI n’utilise pas vos données personnelles et s’engage à supprimer celles
        que vous pourriez intégrer par erreur. Elle peut utiliser certaines
        informations de connexion pour établir des thématiques et plans d’actions
        partant des statistiques d’usage et des questions posées.
      </p>

      <h2>Avons-nous accès à vos données ?</h2>
      <p>
        Si l’ANSSI peut avoir accès aux données personnelles que vous intégrez dans
        MesQuestionsCyber, celle-ci ne sont pas transmises à aucun destinataire sauf
        en cas d’exigence légale ou judiciaire et sont supprimées dans un délai
        raisonnable.
      </p>
      <h2>Cookies et traceurs</h2>
      <p>
        Un cookie est un fichier déposé sur votre terminal lors de la visite d'un
        site. Il a pour objectif de collecter des informations relatives à votre
        navigation et de vous adresser des services adaptés à votre terminal
        (ordinateur, mobile ou tablette).
      </p>
      <div>
        En application de l'article 5-3 de la directive ePrivacy, transposée à
        l'article 82 de la loi n° 78-17 du 6 janvier 1978 relative à l'informatique,
        aux fichiers et aux libertés, les cookies et traceurs suivent deux régimes
        distincts :
        <ul>
          <li>
            D'une part, les cookies strictement nécessaires au service ou ayant pour
            finalité exclusive de faciliter la communication par voie électronique,
            sont dispensés de consentement préalable (article 82 susvisé).
          </li>
          <li>
            D'autre part, les cookies n'étant pas strictement nécessaires au service
            ou n'ayant pas pour finalité exclusive de faciliter la communication par
            voie électronique, doivent être consenti par l'utilisateur. Ce
            consentement de la personne concernée constitue une base légale au sens
            du RGPD (article 6-1 a).
          </li>
        </ul>
      </div>
      <p>
        MesQuestionsCyber ne dépose que des cookies et traceurs strictement
        nécessaires au fonctionnement du service et la solution de mesure d'audience
        "Matomo", configurée en mode "exempté" et ne nécessitant pas de recueil du
        consentement, conformément aux recommandations de la CNIL.
      </p>
      <p>
        (case cochée) Vous êtes suivi(e) de manière anonyme. Décochez cette case pour
        vous exclure du suivi.
      </p>
      <div>
        Pour en savoir plus sur les cookies :
        <ul>
          <li>
            <a
              href="https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/que-dit-la-loi"
              target="_blank"
              >Cookies et traceurs : que dit la loi ?
            </a>
          </li>
          <li>
            <a
              href="https://www.cnil.fr/fr/cookies-et-autres-traceurs/comment-se-proteger/maitriser-votre-navigateur"
              target="_blank"
            >
              Cookies : les outils pour les maîtriser
            </a>
          </li>
        </ul>
      </div>
    </div>
  </dsfr-container>
</main>

<PiedDePage />

<style>
  .conteneur {
    padding: 2rem 0 3.5rem;
  }
</style>
