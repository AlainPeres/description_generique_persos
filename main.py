"""
Génération de personnages de jeu de rôle (multi-systèmes) avec Pydantic.

Architecture :
- Un tronc commun (Personnage) partagé par tous les systèmes
- Un bloc "stats" spécifique au système, choisi automatiquement
  grâce à une union discriminée sur le champ "systeme"
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from pydantic import BaseModel, Field
from typing import Literal, Union, Dict, List
import json


# ---------------------------------------------------------------------------
# Bloc spécifique : Donjons & Dragons 5e
# ---------------------------------------------------------------------------
class StatsDnD(BaseModel):
    systeme: Literal["dnd5e"]
    classe: str
    race: str
    niveau: int = Field(ge=1, le=20)
    force: int = Field(ge=1, le=20)
    dexterite: int = Field(ge=1, le=20)
    constitution: int = Field(ge=1, le=20)
    intelligence: int = Field(ge=1, le=20)
    sagesse: int = Field(ge=1, le=20)
    charisme: int = Field(ge=1, le=20)
    classe_armure: int
    points_de_vie: int
    sorts: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Bloc spécifique : L'Appel de Cthulhu
# ---------------------------------------------------------------------------
class StatsCthulhu(BaseModel):
    systeme: Literal["cthulhu"]
    profession: str
    sante_mentale: int = Field(ge=0, le=99)
    points_de_vie: int
    competences: Dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tronc commun
# ---------------------------------------------------------------------------
class Personnage(BaseModel):
    nom: str
    joueur: str
    historique: str = ""
    stats: Union[StatsDnD, StatsCthulhu] = Field(discriminator="systeme")


# ---------------------------------------------------------------------------
# Création des personnages
# ---------------------------------------------------------------------------
thorin = Personnage(
    nom="Thorin Forgefer",
    joueur="Marie",
    historique="Nain forgeron exilé de sa montagne",
    stats=StatsDnD(
        systeme="dnd5e",
        classe="Guerrier",
        race="Nain",
        niveau=3,
        force=16,
        dexterite=12,
        constitution=15,
        intelligence=10,
        sagesse=11,
        charisme=8,
        classe_armure=17,
        points_de_vie=28,
        sorts=[],
    ),
)

eleanor = Personnage(
    nom="Eleanor Whitfield",
    joueur="Tom",
    historique="Bibliothécaire à Arkham",
    stats=StatsCthulhu(
        systeme="cthulhu",
        profession="Bibliothécaire",
        sante_mentale=65,
        points_de_vie=11,
        competences={
            "Bibliotheque": 70,
            "Psychologie": 45,
            "Tir": 25,
        },
    ),
)


# ---------------------------------------------------------------------------
# Affichage : templates JSON générés + JSON Schema global
# ---------------------------------------------------------------------------
def afficher_separateur(titre: str) -> None:
    print("\n" + "=" * 60)
    print(titre)
    print("=" * 60)


def exporter_json(chemin: str, contenu: str) -> None:
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"  -> exporté : {chemin}")


if __name__ == "__main__":
    afficher_separateur("PERSONNAGE D&D 5e (JSON généré)")
    print(thorin.model_dump_json(indent=2))

    afficher_separateur("PERSONNAGE CTHULHU (JSON généré)")
    print(eleanor.model_dump_json(indent=2))

    afficher_separateur("JSON SCHEMA (commun aux deux systèmes)")
    print(json.dumps(Personnage.model_json_schema(), indent=2, ensure_ascii=False))

    afficher_separateur("EXPORT FICHIERS JSON")
    exporter_json("thorin.json", thorin.model_dump_json(indent=2))
    exporter_json("eleanor.json", eleanor.model_dump_json(indent=2))
    exporter_json("schema_personnage.json", json.dumps(Personnage.model_json_schema(), indent=2, ensure_ascii=False))

    afficher_separateur("VALIDATION : rechargement depuis du JSON brut")
    brut = eleanor.model_dump_json()
    relu = Personnage.model_validate_json(brut)
    print(f"Personnage relu : {relu.nom} ({relu.stats.systeme})")

    afficher_separateur("VALIDATION : erreur si données incohérentes")
    try:
        Personnage(
            nom="Test",
            joueur="X",
            stats={"systeme": "dnd5e", "classe": "Mage"},  # champs manquants
        )
    except Exception as e:
        print(f"Erreur détectée comme attendu :\n{e}")