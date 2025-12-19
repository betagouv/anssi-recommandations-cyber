import { describe, expect, it } from "vitest";
import { ValidateurQuestionUtilisateur } from "../../src/composants/ValidateurQuestionUtilisateur";

describe("Le validateur de la question utilisateur", () => {
  const validateur = new ValidateurQuestionUtilisateur();

  describe("vérifie que les données'", () => {
    it("sont invalides lorsque son la question est vide", () => {
      expect(validateur.estValide("   ")).toBeFalsy();
    });

    it("sont invalides lorsque la question contient plus de 5000 caractère", () => {
      expect(validateur.estValide("mots".repeat(1251))).toBeFalsy();
    });
  });
  describe("permet de renvoyer spécifiquement une erreur", () => {
    it("'La question est obligatoire' lorsque la question est vide", () => {
      const erreurs = validateur.valide(" ");
      expect(erreurs).toEqual("La question est obligatoire");
    });

    it("La question ne peut contenir que 5000 caractères maximum", () => {
      const erreurs = validateur.valide("mots".repeat(1251));
      expect(erreurs).toEqual(
        "La question ne peut contenir que 5000 caractères maximum",
      );
    });
  });
});
