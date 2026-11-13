# Logique du projet

## Le but

- Décrire **un personnage de jeu de rôle**, pour un grand nombre de systèmes
  (D&D 5e, Pathfinder 1, L'Appel de Cthulhu, Fate, SagaS, Daredevils, OpenQuest 3, sans règles…), avec **un seul modèle
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
   | `attributes`                                                                       | valeurs chiffrées, avec une catégorie                                              |
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
(nom, portée, sources). Chaque information est nommée, validée, et ne peut pas
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
`derived_values` : une liste de `DerivedValue` (nom, portée, sources ou
formule). La portée (`applies_to`) dit si la valeur est unique pour le
personnage (`character`, par exemple les PV maximum) ou si la formule
s'applique à **chaque attribut d'une catégorie** (`Main`, `Secondary`, `Talent` ou `State` ; par exemple `Main` pour les modificateurs
de caractéristique en D&D, les jets de sauvegarde en Daredevils) ou à
**chaque compétence** (`skill`, par exemple le BCS en Daredevils, le niveau
d'apprentissage en SagaS, l'expertise en OpenQuest). La liste sert aussi de cahier des charges au calculateur extérieur. Comme
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
| SagaS      | `skill level (associated attribute + learning level)`   |
| Daredevils | `score (0 or more); BCS = score / 5, rounded down`      |
| OpenQuest  | `percentage (0-100)`                                    |

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

En SagaS, les caractéristiques secondaires se calculent **en permanence** à
partir des caractéristiques principales et des points de création achetés :
si une caractéristique principale change, la secondaire change aussi.

- Initiative = (Agilité + Astuce) / 2 + bonus de création ;
- Combat au contact = (Force + 2 × Agilité + Instinct + Volonté) / 5 + bonus
  de création ;
- Combat à distance = (3 × Dextérité + 2 × Instinct) / 5 + bonus de
  création ;
- Vitesse = base de l'espèce (6 pour un humain) + (Endurance + Agilité) /
  4 + bonus de création.

Le total et le bonus se déduisent l'un de l'autre sans ambiguïté (bonus =
total − partie calculée). Comme le JSON doit pouvoir être lu par un humain,
c'est la **valeur finale** qui est stockée (Initiative 5, Vitesse 8… dans le
modèle de fiche, pour un bonus de 0), et les quatre bonus de création
figurent dans `derived_values`. En contrepartie, un total doit être
recalculé quand une caractéristique principale change, à bonus constant.
La classe sociale se décrit, si besoin, dans `occupation`, et l'espèce dans
`description` : ni l'une ni l'autre n'a de champ propre.

En SagaS toujours, et pour la même raison, la `value` d'une compétence est
son **niveau de compétence**, la valeur jouée (caractéristique associée +
niveau d'apprentissage). Le niveau d'apprentissage, acheté avec des points,
s'en déduit sans ambiguïté (niveau − caractéristique associée) et figure dans
`derived_values` ; un niveau doit être recalculé quand sa caractéristique
change, à niveau d'apprentissage constant. Contrairement à PF1, où le total
dépend de bonus absents de la fiche (dons, objets…), rien ne se perd. Dans
le modèle de fiche, toutes les caractéristiques valent 5 (Vitesse 8) : le
niveau est donc la caractéristique plus le niveau d'apprentissage initial
(Esquive 5, Acrobaties −10, Course 8…). La caractéristique associée figure
dans `Skill.base` (par exemple `"base": "Agility"`) : fixée par les règles
pour les compétences de la liste, elle est remplie dans le modèle de fiche,
et une compétence créée par le joueur et l'arbitre (`New`) doit déclarer
celle qu'ils choisissent. `Character` vérifie que `base` désigne une seule
caractéristique, parmi les 8 principales et les 4 secondaires.

En Daredevils, la `value` d'une compétence est son **score** (0 ou plus, sans maximum) : la
chance de base de réussite (BCS = score / 5, arrondi vers le bas) se calcule.
Un score de **0 veut dire compétence non acquise** : contrairement à Cthulhu
ou OpenQuest, il n'y a pas de score de base, le personnage se rabat sur son
Talent brut ou ses attributs. Une compétence acquise (à la création ou plus
tard) reçoit un score initial, attribut gouvernant + second attribut +
Talent gouvernant, calculé avec les valeurs du moment ; elle progresse
ensuite seule. Un changement d'attribut ne la modifie pas : dans l'exemple
de création du livre, les points d'attribut sont répartis après le calcul
des compétences sans les changer, et la blessure grave ajoute un malus de
BCS séparé de la baisse de Dextérité et de Vitesse. Le score stocké n'a donc
pas de part dérivée. Dans le modèle de fiche, les 87 compétences sont à 0
(non acquises). Les attributs sont
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
est retenu, car tous les exemples chiffrés le suivent. La formule du score
initial figure dans `Skill.base` (par exemple `"Deftness + Wit +
Natural"`) : d'après les règles, son premier attribut est l'**attribut
gouvernant** et son premier Talent le **Talent gouvernant**, qui sert à
l'apprentissage par la pratique. Elle est remplie dans le modèle de fiche
(pour Pathology, le livre donne Wit + Wit + Scientific dans le résumé et
Wit + Deftness + Scientific dans la description : la description est
retenue) et obligatoire pour une compétence `New` ajoutée par l'arbitre ;
`Character` vérifie qu'elle commence par un attribut et contient un Talent,
ainsi que les scores (jamais négatifs) et les noms de
`freely_improvable_skills`. Les finances, diplômes, grade, casier, licences
et contacts se décrivent dans `background` ; la Réputation n'est pas
modélisée, ses règles ne figurant pas dans le livre. Sauf mention contraire, Daredevils
arrondit au plus proche (3,5 donne 4), contrairement à SagaS.

En OpenQuest 3, la `value` d'une compétence est son **pourcentage total**
(sa formule de base, par exemple `"Dexterity + 10"`, figure dans
`Skill.base`)
(base + points de création + croissance), la valeur jouée ; la croissance
s'ajoute au total. Les extraits du SRD ne disent pas si la base (somme de
caractéristiques) est recalculée quand une caractéristique augmente ; le
texte sur la croissance des caractéristiques (« overcome the innate
weaknesses ») et la filiation RuneQuest le laissent penser, ce qui reste à
confirmer. Dans ce cas, la part acquise serait dérivée (total − base).
`Character` vérifie
qu'il reste entre 0 et 100, la limite des règles. Les maximums de PV
((TAI + CON) / 2, arrondi au-dessus) et de PM (POU), le modificateur de
dégâts, le mouvement et le niveau d'expertise se calculent ; seuls les PV
et PM actuels sont stockés. Le bloc spécifique porte le concept, les points
de fortune et de croissance non dépensés, les motivations (`Motive` : texte,
de saga ou de quête, mise en jeu — l'astérisque —, accomplie), la religion,
le rang et le statut de lanceur spécialiste en texte libre, et les sorts de
magie divine déjà lancés, qui restent dépensés jusqu'à leur récupération
(`divine_spells_cast`, vérifiés contre les `Ability` de catégorie `Spell`).
Les sorts sont des `Ability` `Spell` dont la `value` est la magnitude. Une
créature non humaine décrit son espèce dans `description`, ses traits et
armes naturelles dans `abilities`.

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

## Les catégories

`AttributeCategory` dit **de quelle nature** est une valeur chiffrée, ce qui
rend le JSON lisible et précise la portée des valeurs dérivées :

- `Main` : les caractéristiques (Force, DEX, Wit…) ;
- `Secondary` : les autres valeurs durables, le plus souvent fondées sur
  les principales (Initiative SagaS, Off-hand Dexterity, PV maximum tirés
  aux dés en D&D et PF1, Move en Cthulhu) ;
- `Talent` : les aptitudes (Talents de Daredevils) ;
- `State` : les valeurs actuelles qui changent en jeu (PV, Santé, blessures,
  dégâts).

La catégorie est fixée par les règles et répétée dans chaque personnage :
c'est le prix de la lisibilité. Elle est obligatoire, pour qu'aucun attribut
ne soit classé par défaut sans qu'on l'ait décidé.

Pour les compétences et les capacités, deux axes indépendants :

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
