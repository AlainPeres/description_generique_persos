# Logique du projet

## Le but

Décrire **n'importe quel personnage de jeu de rôle**, quel que soit le système
(D&D 5e, L'Appel de Cthulhu, Fate, SagaS, sans règles…), avec **un seul modèle
Python** (`Character`, Pydantic v2), puis l'exporter et le relire en JSON.

## L'idée centrale : deux couches

Un personnage se décompose en deux parties.

1. **Une couche générique**, commune à tous les systèmes. Presque tout ce
   qu'on trouve sur une fiche se ramène à des listes de « nom + valeur » :

   | Champ | Contenu |
   | --- | --- |
   | `name`, `description`, `age`, `occupation`, `background`, `additional_information` | texte libre |
   | `attributes` | caractéristiques chiffrées (FOR, DEX, PV…) |
   | `skills` | compétences, avec une catégorie |
   | `abilities` | dons, pouvoirs, avantages, sorts… |
   | `equipment` | objets, armes, armures, consommables |

2. **Une couche spécifique** (`specific_values`), facultative. Elle contient ce
   qui ne rentre pas dans « nom + valeur » : la classe et la race en D&D, les
   aspects et le stress en Fate, des tags libres en sans règles…

Règle de répartition : **si une donnée peut s'écrire « nom + valeur », elle va
dans la couche générique**. La couche spécifique reste aussi petite que
possible.

Exception : les compteurs de progression ou de gestion (niveau et XP en D&D,
points de création non utilisés en SagaS) vont dans la couche spécifique.
Ce ne sont pas des caractéristiques utilisées pour les jets, et le bloc
spécifique permet de les valider (par exemple `ge=0`).

Les valeurs qui se calculent directement à partir d'autres valeurs ne sont
pas stockées : Idée, Chance et Connaissance en Cthulhu (INT×5, POU×5,
ÉDU×5), bonus aux dégâts, maximums de SAN, PV et PM, bonus de maîtrise en
D&D… Les stocker créerait un risque d'incohérence quand la valeur source
change. Les valeurs *actuelles* (SAN, PV et PM restants) ne se calculent pas
et, elles, sont stockées.

Les coches d'amélioration de compétence (Cthulhu et autres jeux BRP) sont
portées par la compétence elle-même : `Skill.checked`. `None` veut dire que
le système n'a pas de coches (le champ n'apparaît alors pas dans le JSON),
`False`/`True` qu'elle est décochée ou cochée.

## Les catégories : deux axes indépendants

- `SkillCategory` dit **d'où vient** une entrée :
  - `Base` : elle fait partie de la liste officielle du système ;
  - `New` : le joueur l'a ajoutée. C'est le cas des armes de contact en
    Cthulhu : elles ne figurent pas dans le modèle de fiche, chaque joueur
    ajoute celles qu'il utilise ;
  - `Generic` et `Specialization` : compétences ouvertes, comme *Art (…)* ou
    *Pilotage (…)*.
- `AbilityCategory` dit **de quel type** est une capacité : Feat, Power,
  Advantage, Spell…

Une `Ability` porte donc les deux : `category` pour son type, `origin` pour sa
provenance. **Un sort n'est pas un modèle à part** : c'est une `Ability` avec
`category=Spell`, et son effet va dans `description`.

## Comment Pydantic sait de quel système il s'agit

Chaque bloc spécifique a un champ `system` à valeur fixe
(`Literal["dnd5e"]`, `Literal["fate"]`…). `specific_values` est une **union
discriminée** : en lisant un JSON, Pydantic regarde `system` et choisit
directement la bonne classe.

Cette union, `SpecificValues`, est écrite en clair à la fin de
`systems/specific_values.py`, à côté des classes qu'elle liste, et
`models.py` se contente de l'importer. Ajouter un système ne demande donc
**jamais** de modifier `models.py`. L'écrire en clair permet aussi à
l'éditeur (Pylance, mypy) de connaître chaque classe et de compléter leurs
champs.

## Organisation des fichiers

```text
strict_model.py           StrictModel, la classe de base commune
models.py                 le schéma : Character et ses sous-modèles
systems/
├── specific_values.py    les blocs SpecificValuesX + l'union SpecificValues
└── <jeu>.py              un personnage générique par système (generic_<jeu>)
main.py                   exporte les JSON et vérifie la relecture
```

Les dépendances vont dans un seul sens, ce qui évite les imports circulaires :

```text
strict_model.py  ──►  specific_values.py  ──►  models.py  ──►  systems/<jeu>.py  ──►  main.py
(pydantic seul)       (blocs spécifiques)       (Character)     (generic_<jeu>)        (export)
```

`specific_values.py` ne dépend que de Pydantic et de `strict_model.py`,
jamais de `Character`. C'est pour ça que les blocs spécifiques y sont, et pas
dans `models.py` ni dans chaque `<jeu>.py`.

## Champs inconnus refusés

Tous les modèles héritent de `StrictModel`, qui fixe `extra="forbid"`. Un
champ que le modèle ne connaît pas (faute de frappe, champ supprimé comme
l'ancien `Stunts` de Fate) provoque une erreur de validation au lieu d'être
ignoré sans prévenir.

## Ce que produit `python main.py`

1. **Un modèle de fiche par système** (`generic_<jeu>.json`) : la structure
   complète, la liste officielle des compétences, et des valeurs par défaut à
   remplacer (`"to be specified"`).
2. **`schema_character.json`** : le JSON Schema de `Character`. Il décrit la
   forme d'une fiche valide pour des outils extérieurs à Python (éditeur,
   autre langage, formulaire, LLM). Il ne contient ni le sens des champs ni
   les listes de compétences.
3. **Une vérification** : chaque modèle exporté est relu avec
   `Character.model_validate_json` et comparé à l'original.

## Champs facultatifs et exclusion à l'export

Tous les champs de `Character` ont une valeur par défaut (`""`, `None` ou
`[]`). Un système ne remplit que ce qu'il utilise, et un JSON peut omettre
tout le reste.

Pour qu'un champ inutile n'apparaisse pas dans le JSON exporté :

- `exclude={"attributes", "skills", "abilities"}` retire les champs nommés (c'est ce que
  fait `norules`) ;
- `exclude_defaults=True` retire tout champ resté à sa valeur par défaut.

Un champ exclu reprend sa valeur par défaut quand on relit le JSON.

## Ajouter un système

1. Dans `systems/specific_values.py`, créer `SpecificValuesXxx(StrictModel)` avec
   `system: Literal["xxx"]`, puis l'ajouter à l'union `SpecificValues`.
2. Créer `systems/xxx.py` avec un `generic_xxx = Character(...)`, en mettant
   le maximum de données dans les listes génériques.
3. Dans `main.py`, importer `generic_xxx` et l'ajouter à la liste `EXPORTS`.
