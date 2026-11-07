# Logique du projet

## Le but

- Décrire **un personnage de jeu de rôle**, pour un grand nombre de systèmes
  (D&D 5e, Pathfinder 1, L'Appel de Cthulhu, Fate, SagaS, Daredevils, sans règles…), avec **un seul modèle
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
   | `conditions`                                                                       | effets durables physiques, mentaux ou autres (`Condition`)                         |

2. **Une couche spécifique** (`specific_values`), facultative. Elle contient ce
   qui ne rentre pas dans « nom + valeur » : les classes (multiclasse,
   sous-classes ou archétypes) et la race en D&D et Pathfinder, les aspects
   et le stress en Fate, des tags libres en sans règles…

Règle de répartition : **si une donnée peut s'écrire « nom + valeur », elle va
dans la couche générique**. La couche spécifique reste aussi petite que
possible.

Exception : les compteurs de progression ou de gestion (niveaux de classe et
XP en D&D et PF1, points de création non utilisés en SagaS) vont dans la couche
spécifique. Ce ne sont pas des caractéristiques utilisées pour les jets, et
le bloc spécifique permet de les valider (par exemple `ge=0`). Les points de
création SagaS ne contredisent pas le but de description : ce sont des points
mis de côté pour plus tard, donc un état du personnage.

Quand un élément regroupe plusieurs informations, il devient un petit modèle
plutôt qu'un tuple ou des listes parallèles : `DnDClass` (nom, sous-classe,
niveau), `PF1Class` (nom, archétypes, niveau, sorts restants),
`PreparedSpell` (nom, niveau, lancé), `Condition` (nom, nature, durée,
description, guéri), `StressBox` et `Consequence` en Fate, `DerivedValue`
(nom, sources). Chaque information est nommée, validée, et ne peut pas
se désynchroniser des autres.

`DnDClass` et `PF1Class` héritent d'une base commune, `CharacterClass` (nom,
niveau 1–20), sur laquelle porte aussi le contrôle d'unicité des noms de
classe. Chaque système ajoute ses propres champs : une sous-classe unique en
D&D, des archétypes cumulables et des sorts par classe en PF1. Une classe
unique aux champs facultatifs aurait accepté, par exemple, des sorts préparés
par classe en D&D, où les emplacements sont partagés. Un futur système à
classes réutilisera la base.

**Seul est stocké ce qui ne peut pas être calculé à partir des autres
valeurs** : Idée, Chance et Connaissance en Cthulhu (INT×5, POU×5, ÉDU×5),
bonus aux dégâts, maximums de SAN, PV et PM en Cthulhu, bonus de maîtrise et
niveau total en D&D (somme des niveaux de classe), classe d'armure en D&D et
en PF1 (calculée à partir de la classe, de la race, de l'armure, du
bouclier, des objets et des sorts actifs), protection et bonus d'impact
maximum, points de vie, seuils de choc et défense réflexe en SagaS… ne
figurent pas sur la fiche. Les stocker créerait un risque d'incohérence quand
la valeur source change. Ils sont calculés **à l'extérieur du modèle**, par
les outils qui lisent le personnage.

En revanche, sont stockés :

- les valeurs *actuelles* (`Current Sanity`, `Current Hit Points`, blessures
  et étourdissement en SagaS…), qui évoluent en jeu ;
- les maximums qui ne se calculent pas, comme les PV maximum en D&D et en
  PF1, tirés aux dés à chaque niveau (`Maximum Hit Points`) ;
- la disponibilité des cases de stress et des conséquences en Fate
  (`StressBox.available`, `Consequence.available`). Fate Core en donne une
  valeur de départ à partir de Physique ou de Volonté, mais une prouesse, un
  extra ou une décision hors règles peut la changer, et aucun calculateur ne
  peut prévoir toutes ces possibilités : elle n'est donc pas dérivable.

Pour que le lecteur du JSON sache quelles valeurs existent sans être
stockées, chaque bloc spécifique les liste dans un champ fixe
`derived_values` : une liste de `DerivedValue` (nom, sources ou formule),
qui sert aussi de cahier des charges au calculateur extérieur. Comme
`skill_value_meaning`, il a une valeur par défaut, apparaît dans chaque JSON
et toute autre valeur est refusée. Un `Literal` ne pouvant pas contenir de
liste, c'est le validateur `fixed(...)` qui reproduit ce comportement. Fate
et le système sans règles n'en ont pas : rien n'y est dérivé.

Le sens de `Skill.value` est une **convention fixe par système**, choisie par
le modèle (ce ne sont pas les règles du jeu qui l'imposent). Chaque bloc
spécifique d'un système à compétences la déclare dans un champ
`skill_value_meaning` à valeur unique (`Literal`), comme `system` : il a une
valeur par défaut, apparaît dans chaque JSON pour que le fichier s'explique
seul, et toute autre valeur est refusée.

| Système    | `skill_value_meaning`                                   |
| ---------- | ------------------------------------------------------- |
| D&D 5e     | `proficiency level: 0 none, 1 proficient, 2 expertise`  |
| PF1        | `ranks`                                                 |
| Cthulhu    | `percentage`                                            |
| Fate       | `rating on the Fate ladder`                             |
| SagaS      | `learning level`                                        |
| Daredevils | `score (0 or more); BCS = score / 5, rounded down`      |

En D&D 5e, la `value` d'une compétence est donc son **niveau de maîtrise**
(0 = aucune, 1 = maîtrise, 2 = expertise), et non son bonus total : celui-ci
se calcule à partir du modificateur de caractéristique et du bonus de
maîtrise, qui dépend du niveau total. Une montée de niveau ne demande ainsi
aucune correction des compétences.

Toujours en D&D 5e, les caractéristiques sont stockées à leur valeur
**permanente**. Les points perdus jusqu'à un repos ou une restauration
(*Strength Drain* de l'Ombre, *Feeblemind*…) vont dans `ability_reduction`,
et la valeur actuelle se calcule, comme `attribute_loss` en Daredevils. Une
perte définitive, elle, se traite en modifiant directement la caractéristique.

En Pathfinder 1, la `value` d'une compétence est son **nombre de rangs** :
ce sont des choix du joueur, impossibles à recalculer. Le total (modificateur
de caractéristique, +3 de compétence de classe, dons, objets, malus
d'armure…) se calcule, et le stocker seul ferait perdre les rangs, donc par
exemple la possibilité d'utiliser une compétence réservée aux personnages
formés. De même, BBA, jets de sauvegarde, BMO et DMD ne sont pas stockés.

En SagaS, les caractéristiques secondaires (Initiative, Combat au contact,
Combat à distance, Vitesse) sont **stockées** comme les principales : leur
formule ne sert qu'à les initialiser à la création, ensuite elles évoluent
comme les principales. La classe sociale se décrit, si besoin, dans
`occupation`, et l'espèce dans `description` : ni l'une ni l'autre n'a de
champ propre.

En SagaS toujours, pour la même raison que PF1, la `value` d'une compétence
est son **niveau d'apprentissage**. Le niveau de compétence (attribut associé + niveau
d'apprentissage) se calcule ; l'attribut associé à chaque compétence de la
liste est fixé par les règles, il n'est donc pas stocké dans le personnage.
Une compétence créée par le joueur et l'arbitre (`New`) est rattachée à la
caractéristique qu'ils choisissent : c'est une donnée du personnage, portée
par `Skill.attribute` (absent du JSON quand il vaut `None`). `Character`
vérifie qu'une compétence `New` a bien un `attribute` parmi les 8
caractéristiques principales et les 4 secondaires, et qu'aucune compétence
de la liste n'en déclare.

En Daredevils, la `value` d'une compétence est son **score** (0 ou plus, sans maximum) : la
chance de base de réussite (BCS = score / 5, arrondi vers le bas) se calcule,
et la formule du score initial ne sert qu'à la création. Les attributs sont
stockés à leur valeur **permanente** ; les points perdus (blessures,
maladie) vont dans `attribute_loss`, et la valeur actuelle se calcule, comme
l'affaiblissement en PF1. Les Talents (règle avancée) sont des attributs
comme les autres, à 0 dans le modèle de fiche. La dextérité de la main non
directrice est initialisée à la création puis améliorée seule : elle est
stockée. La règle optionnelle d'amélioration des attributs par
l'apprentissage accumule des fractions (+0,5 par point de BCS gagné ; le
texte dit 0,05 mais son exemple donne 0,5) : le cumul en cours est stocké
dans `attribute_progress`. Les dégâts létaux et non létaux sont des
attributs ; les **dégâts critiques**, eux, se comptent par localisation (les
12 de la table de localisation), ne s'ajoutent pas au total et rendent la
partie du corps inutilisable jusqu'à guérison : ils vont dans
`critical_damage`. Les points de **Chance** (règle optionnelle, tirés avant
chaque aventure) restants vont dans `luck_points`, `None` voulant dire que
la règle n'est pas utilisée. Le livre se contredit sur le total de
résistance aux dégâts (DRT) : le §1.3.2 additionne Santé, Force et Volonté,
le glossaire donne Santé + Force / 2 + Volonté / 2. C'est le glossaire qui
est retenu, car tous les exemples chiffrés le suivent. Comme en SagaS, une
compétence `New` ajoutée par l'arbitre déclare son attribut gouvernant
(`Skill.attribute`) et, propre à Daredevils, son **Talent gouvernant**
(`Skill.talent`), qui sert à l'apprentissage par la pratique ; `Character`
le vérifie, ainsi que les scores (jamais négatifs) et les noms de
`freely_improvable_skills`. Les finances, diplômes, grade, casier, licences
et contacts se décrivent dans `background` ; la Réputation n'est pas
modélisée, ses règles ne figurant pas dans le livre. Sauf mention contraire, Daredevils
arrondit au plus proche (3,5 donne 4), contrairement à SagaS.

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
- dans ces dictionnaires d'emplacements, **un niveau absent veut dire que
  tous ses emplacements sont disponibles** : après un repos long, on a `{}`,
  et un niveau épuisé s'écrit `0`. Exemple : un magicien 5 qui a lancé deux
  *Bouclier* et deux *Boule de feu* a `{1: 2, 3: 0}` ;
- en D&D, lancer un sort préparé consomme **un emplacement, pas le sort** :
  tous les `prepared_spells` restent disponibles tant qu'il reste un
  emplacement de niveau suffisant. En PF1 au contraire, chaque exemplaire
  préparé est consommé (`PreparedSpell.cast`) ;
- toujours en D&D, les `Ability` de catégorie `Spell` disent quels sorts le
  personnage **connaît** (avec leur effet), `prepared_spells` lesquels il peut
  lancer **aujourd'hui**, et `spell_slots_remaining` **combien de fois**.
  `prepared_spells` vide veut dire que tous les sorts connus sont
  disponibles : on ne le remplit que pour les classes qui connaissent plus de
  sorts qu'elles n'en préparent (magicien). `Character` vérifie que chaque
  nom de `prepared_spells` correspond à une `Ability` de catégorie `Spell`,
  sans tenir compte de la casse ;
- ressources de classe : `resources_remaining`, un dictionnaire aux noms
  libres (`{"Ki": 3}`) plutôt qu'un champ par ressource. Les sorts lancés
  une fois par repos sans emplacement (sorts raciaux, de dons, *Mystic
  Arcanum*…) y figurent aussi, sous le nom du sort ;
- compteurs propres au système : épuisement, réduction de caractéristique
  (`ability_reduction`), inspiration et dés de vie en D&D ; affaiblissement,
  diminution, niveaux négatifs et points d'héroïsme en PF1.

Les effets durables vont dans `Character.conditions`, une liste de
`Condition` commune à tous les systèmes : nom, nature (`kind`), durée
facultative (`temporary`, `indefinite` ou `permanent`), description, et
`cured`, conservé pour l'histoire du personnage. La nature vaut :

- `Physical` : blessure, maladie, poison… dont les **blessures graves
  physiques** de SagaS ;
- `Mental` : les **troubles mentaux** de Cthulhu, et ce que SagaS appelle
  **psychique** (*Psychical*) : une blessure grave psychique de SagaS est
  une `Condition` de nature `Mental` ;
- `Other` : malédiction, sort de longue durée, effet magique…

Les états chiffrés que les règles exploitent restent dans le bloc
spécifique : épuisement et `ability_reduction` en D&D, affaiblissement,
diminution et niveaux négatifs en PF1, conséquences en Fate,
`attribute_loss` en Daredevils.

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
provenance. `origin` vaut `Base` par défaut (capacité des règles officielles)
ou `New` (ajoutée par le joueur ou le MJ : sort maison, prouesse inventée,
super-pouvoir hors règles…) ; `Generic` et `Specialization` n'ont pas de sens
pour une capacité. Ce champ est purement descriptif : aucun validateur ne le
lit. **Un sort n'est pas un modèle à part** : c'est une `Ability` avec
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
models.py                 le schéma : Character, ses sous-modèles et les contrôles
                          entre les deux couches
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
   autre langage, formulaire, LLM). Il contient aussi, comme valeurs fixes,
   le sens de `Skill.value` (`skill_value_meaning`) et la liste des valeurs
   dérivées (`derived_values`) de chaque système, mais pas les listes de
   compétences, ni les contrôles faits par `Character` (sorts préparés en
   D&D, attributs des compétences nouvelles en SagaS).
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
   compétences, `derived_values` s'il a des valeurs dérivées), puis
   l'ajouter à l'union `SpecificValues`.
2. Créer `systems/xxx.py` avec un `generic_xxx = Character(...)`, en mettant
   le maximum de données dans les listes génériques.
3. Dans `main.py`, importer `generic_xxx` et l'ajouter à la liste `EXPORTS`.
