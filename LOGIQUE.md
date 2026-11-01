# Logique du projet

## Le but

- Décrire **un personnage de jeu de rôle**, pour un grand nombre de systèmes
  (D&D 5e, Pathfinder 1, L'Appel de Cthulhu, Fate, SagaS, sans règles…), avec **un seul modèle
  Python** (`Character`, Pydantic v2), puis l'exporter et le relire en JSON.

- Rendre plus simple **l'introduction d'un nouveau système**.

- Produire un schéma JSON permettant de vérifier qu'un **JSON de personnage est conforme au modèle**.

- **Attention :** ce n'est pas un outil de création de personnage, mais un outil de description.

## L'idée centrale : deux couches

Un personnage se décompose en deux parties.

1. **Une couche générique**, commune à tous les systèmes. Presque tout ce
   qu'on trouve sur une fiche se ramène à des listes de « nom + valeur » :

   | Champ                                                                              | Contenu                                                                            |
   | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
   | `name`, `description`, `age`, `occupation`, `background`, `additional_information` | texte libre                                                                        |
   | `attributes`                                                                       | caractéristiques chiffrées (FOR, DEX, PV…)                                         |
   | `skills`                                                                           | compétences, avec une catégorie                                                    |
   | `abilities`                                                                        | dons, pouvoirs, avantages, sorts…                                                  |
   | `equipment`                                                                        | objets, armes, armures, consommables, monnaie (la somme est la quantité)           |
   | `possessions`                                                                      | biens qui ne sont pas de l'équipement transporté (maison, terres…), en texte libre |
   | `conditions`                                                                       | effets durables, en texte libre                                                    |

2. **Une couche spécifique** (`specific_values`), facultative. Elle contient ce
   qui ne rentre pas dans « nom + valeur » : les classes (multiclasse,
   sous-classes ou archétypes) et la race en D&D et Pathfinder, les troubles mentaux en Cthulhu, les
   aspects et le stress en Fate, les blessures graves en SagaS, des tags
   libres en sans règles…

Règle de répartition : **si une donnée peut s'écrire « nom + valeur », elle va
dans la couche générique**. La couche spécifique reste aussi petite que
possible.

Exception : les compteurs de progression ou de gestion (niveaux de classe et
XP en D&D, points de création non utilisés en SagaS) vont dans la couche
spécifique. Ce ne sont pas des caractéristiques utilisées pour les jets, et
le bloc spécifique permet de les valider (par exemple `ge=0`). Les points de
création SagaS ne contredisent pas le but de description : ce sont des points
mis de côté pour plus tard, donc un état du personnage.

Quand un élément regroupe plusieurs informations, il devient un petit modèle
plutôt qu'un tuple ou des listes parallèles : `DnDClass` (nom, sous-classe,
niveau), `PF1Class` (nom, archétypes, niveau), `MentalDisorder` (nom, durée, description, guéri), `StressBox` et
`Consequence` en Fate. Chaque information est nommée, validée, et ne peut pas
se désynchroniser des autres.

**Seul est stocké ce qui ne peut pas être calculé à partir des autres
valeurs** : Idée, Chance et Connaissance en Cthulhu (INT×5, POU×5, ÉDU×5),
bonus aux dégâts, maximums de SAN, PV et PM en Cthulhu, bonus de maîtrise et
niveau total en D&D (somme des niveaux de classe)… ne figurent pas sur la
fiche. Les stocker créerait un risque d'incohérence quand la valeur source
change. En revanche, sont stockés :

- les valeurs *actuelles* (`Current Sanity`, `Current Hit Points`…), qui
  évoluent en jeu ;
- les maximums qui ne se calculent pas, comme les PV maximum en D&D et en
  PF1, tirés aux dés à chaque niveau (`Maximum Hit Points`) ;
- deux **exceptions**, en théorie dérivées mais stockées parce qu'elles
  dépendent de trop de sources pour être recalculées sans moteur de règles :
  - la classe d'armure en D&D et en PF1 (`Armor Class`) : armure, bouclier,
    défense sans armure, objets magiques, sorts… ;
  - la disponibilité des cases de stress et des conséquences en Fate
    (`StressBox.available`, `Consequence.available`) : en Fate Core, elle
    découle du niveau de Physique ou de Volonté, mais les extras, les
    prouesses et les règles maison la modifient souvent.

Le sens de `Skill.value` est une **convention fixe par système**, choisie par
le modèle (ce ne sont pas les règles du jeu qui l'imposent). Chaque bloc
spécifique d'un système à compétences la déclare dans un champ
`skill_value_meaning` à valeur unique (`Literal`), comme `system` : il a une
valeur par défaut, apparaît dans chaque JSON pour que le fichier s'explique
seul, et toute autre valeur est refusée.

| Système  | `skill_value_meaning`                                   |
| -------- | ------------------------------------------------------- |
| D&D 5e   | `proficiency level: 0 none, 1 proficient, 2 expertise`  |
| PF1      | `ranks`                                                 |
| Cthulhu  | `percentage`                                            |
| Fate     | `rating on the Fate ladder`                             |
| SagaS    | `skill score`                                           |

En D&D 5e, la `value` d'une compétence est donc son **niveau de maîtrise**
(0 = aucune, 1 = maîtrise, 2 = expertise), et non son bonus total : celui-ci
se calcule à partir du modificateur de caractéristique et du bonus de
maîtrise, qui dépend du niveau total. Une montée de niveau ne demande ainsi
aucune correction des compétences.

En Pathfinder 1, la `value` d'une compétence est son **nombre de rangs** :
ce sont des choix du joueur, impossibles à recalculer. Le total (modificateur
de caractéristique, +3 de compétence de classe, dons, objets, malus
d'armure…) se calcule, et le stocker seul ferait perdre les rangs, donc par
exemple la possibilité d'utiliser une compétence réservée aux personnages
formés. De même, BBA, jets de sauvegarde, BMO et DMD ne sont pas stockés.

Les coches d'amélioration de compétence (Cthulhu et autres jeux BRP) sont
portées par la compétence elle-même : `Skill.checked`. `None` veut dire que
le système n'a pas de coches (le champ n'apparaît alors pas dans le JSON),
`False`/`True` qu'elle est décochée ou cochée.

## Décrire le personnage entre deux scènes

Le modèle décrit l'état du personnage **entre deux scènes**, pas en plein
combat : jets contre la mort, concentration, conditions d'un tour et PV
temporaires ne sont pas stockés. L'ordre d'initiative, la position ou les
actions du tour appartiennent à la scène, pas au personnage.

Ce qui dure jusqu'au prochain repos est stocké, toujours sous forme de
**valeurs restantes** (les maximums se calculent) :

- emplacements de sort restants : communs à toutes les classes en D&D
  (`spell_slots_remaining`, plus `pact_slots_remaining` pour l'occultiste),
  propres à chaque classe en PF1 (`PF1Class.spells_remaining` pour les
  lanceurs spontanés, `PF1Class.prepared_spells` pour les lanceurs qui
  préparent un sort précis dans chaque emplacement) ;
- ressources de classe : `resources_remaining`, un dictionnaire aux noms
  libres (`{"Ki": 3}`) plutôt qu'un champ par ressource ;
- compteurs propres au système : épuisement, inspiration et dés de vie en
  D&D ; affaiblissement, diminution, niveaux négatifs et points d'héroïsme
  en PF1.

Les effets durables (malédiction, maladie, sort de longue durée) vont dans
`Character.conditions`, une liste de textes libres commune à tous les
systèmes. Les troubles mentaux de Cthulhu et les blessures graves de SagaS
restent à part : ce sont des séquelles, avec leurs propres informations.

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
   `system: Literal["xxx"]` (et `skill_value_meaning` si le système a des
   compétences), puis l'ajouter à l'union `SpecificValues`.
2. Créer `systems/xxx.py` avec un `generic_xxx = Character(...)`, en mettant
   le maximum de données dans les listes génériques.
3. Dans `main.py`, importer `generic_xxx` et l'ajouter à la liste `EXPORTS`.
