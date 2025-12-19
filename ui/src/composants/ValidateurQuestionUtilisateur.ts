import z from "zod";
import { type Validateur } from "./validateur";

type QuestionUtilisateur = string;

export class ValidateurQuestionUtilisateur
  implements Validateur<QuestionUtilisateur>
{
  schema: z.ZodString;

  constructor() {
    this.schema = z
      .string("La question est obligatoire")
      .trim()
      .min(1, "La question est obligatoire")
      .max(5000, "La question ne peut contenir que 5000 caractères maximum");
  }

  valide(jeu: string): string {
    try {
      this.schema.parse(jeu);
      return "";
    } catch (e) {
      const zodError = e as z.ZodError;
      return zodError.issues[0].message;
    }
  }

  estValide(jeu: string): boolean {
    try {
      this.schema.parse(jeu);
      return true;
    } catch {
      return false;
    }
  }
}
