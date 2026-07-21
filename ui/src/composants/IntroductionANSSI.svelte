<script lang="ts">
</script>

<div class="introduction">
  <p>
    🚨 Nous avons besoin de vous pour poser un maximum de questions cyber pour nous
    aider à proposer des réponses de qualité.
  </p>
  <p>
    Pour chaque question posée, merci de lire attentivement la réponse générée, en
    portant une attention particulière aux sources citées. Vos retours nous aideront
    notamment à identifier : des sources non pertinentes ou manquantes, des réponses
    incomplètes ou imprécises, etc...
  </p>
  <p>
    Vous pouvez également contribuer à l’amélioration du service en renseignant, dans
    cette
    <dsfr-link
      label="base de données"
      blank
      href="https://grist.numerique.gouv.fr/o/docs/dSeDbrFjnbTf/Jeu-de-donnees-MQC-Reponses-maitrisees"
    ></dsfr-link>
    (via l'outil GRIST), la réponse que vous auriez attendue, accompagnée des sources associées.
    Ces éléments nous permettront d’enrichir notre base d’évaluation.
  </p>
  <p>
    👯 Rejoignez également notre groupe Tchap dédié à ce test afin d’échanger avec
    l’équipe du Lab, poser vos questions et partager vos retours.
  </p>
</div>

<style lang="scss">
  .introduction {
    box-sizing: border-box;
    max-width: 840px;
    padding: 32px 16px;
    margin: 0 auto 72px;
    display: flex;
    flex-direction: column;
    gap: 16px;

    @media screen and (min-width: 768px) {
      margin-top: 72px;
    }

    ul {
      list-style-type: none;
      padding-left: 0;
      display: flex;
      flex-direction: column;
      gap: 8px;

      li {
        display: flex;
        flex-direction: row;
        gap: 8px;
        align-items: center;

        &:before {
          content: url('/icons/fleche-bas-scroll.svg');
          transform: rotate(-90deg);
          display: flex;
          width: 16px;
          height: 16px;
        }
      }
    }
  }
</style>
