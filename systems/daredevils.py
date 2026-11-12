"""
Generic Daredevils (FGU, 1982) character template.

Default values ("to be specified", 75 attribute points spread evenly, talents
and skill scores of 0) are meant to be replaced when describing an actual
character. Finances, degrees, military rank, criminal record, licenses and
contacts are described in `background`. Reputation is not modeled (its
rules are not in the rulebook).
"""

from models import Character, Attribute, Skill, SkillCategory
from systems.specific_values import SpecificValuesDaredevils

generic_daredevils = Character(
    name="Generic Daredevils Character",
    description="to be specified",
    age="to be specified",
    background="to be specified",
    occupation="to be specified",
    additional_information="to be specified",
    specific_values=SpecificValuesDaredevils(system="daredevils"),
    attributes=[
        # Permanent ratings (1 to 40, 75 points at creation); current ratings
        # are derived from them and specific_values.attribute_loss
        Attribute(name="Wit", value=13),
        Attribute(name="Will", value=13),
        Attribute(name="Strength", value=13),
        Attribute(name="Deftness", value=12),
        Attribute(name="Speed", value=12),
        Attribute(name="Health", value=12),

        # Talents (advanced rule), at most 20
        Attribute(name="Charismatic", value=0),
        Attribute(name="Combative", value=0),
        Attribute(name="Communicative", value=0),
        Attribute(name="Esthetic", value=0),
        Attribute(name="Mechanical", value=0),
        Attribute(name="Natural", value=0),
        Attribute(name="Scientific", value=0),

        # Initialized as (Wit + Will + Deftness) / 6, then improved on its own,
        # so it is stored
        Attribute(name="Off-hand Dexterity", value=6),

        # Current damage, in points; critical damage is kept per location
        # in specific_values.critical_damage
        Attribute(name="Lethal Damage", value=0),
        Attribute(name="Subdual Damage", value=0),
    ],
    # Value = skill score (0 or more, no maximum); the BCS is derived. 0 = skill
    # not acquired: unlike Cthulhu or OpenQuest there is no base score, the
    # character falls back on raw Talent or Attributes. A skill acquired gets
    # its initial score (governing attribute + attribute + governing talent,
    # with the values of the moment), then improves on its own: later changes
    # to the attributes do not affect it. GENERIC skills must be specified:
    # "History (Roman Empire)", "Language (French)"...
    skills=[
        # Practical skills
        Skill(name="Acrobat", category=SkillCategory.BASE, value=0),
        Skill(name="Climbing", category=SkillCategory.BASE, value=0),
        Skill(name="Jumping", category=SkillCategory.BASE, value=0),
        Skill(name="Running", category=SkillCategory.BASE, value=0),
        Skill(name="Swimming", category=SkillCategory.BASE, value=0),
        Skill(name="Cyclist", category=SkillCategory.BASE, value=0),   # motorcycles
        Skill(name="Driver", category=SkillCategory.BASE, value=0),
        Skill(name="Driver, Heavy Equipment", category=SkillCategory.BASE, value=0),
        Skill(name="Gambling", category=SkillCategory.BASE, value=0),
        Skill(name="Horsemanship", category=SkillCategory.BASE, value=0),
        Skill(name="Hunting", category=SkillCategory.BASE, value=0),
        Skill(name="Mimicry", category=SkillCategory.BASE, value=0),
        Skill(name="Pilot", category=SkillCategory.BASE, value=0),
        Skill(name="Pilot, Aerostat", category=SkillCategory.BASE, value=0),
        Skill(name="Seamanship", category=SkillCategory.BASE, value=0),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0),
        Skill(name="Survival", category=SkillCategory.BASE, value=0),
        Skill(name="Throwing", category=SkillCategory.BASE, value=0),
        Skill(name="Tracking", category=SkillCategory.BASE, value=0),

        # Task skills
        Skill(name="Blacksmith", category=SkillCategory.BASE, value=0),
        Skill(name="Carpenter", category=SkillCategory.BASE, value=0),
        Skill(name="Electrician", category=SkillCategory.BASE, value=0),
        Skill(name="Gunsmith", category=SkillCategory.BASE, value=0),
        Skill(name="Machinist", category=SkillCategory.BASE, value=0),
        Skill(name="Cryptography", category=SkillCategory.BASE, value=0),
        Skill(name="Demolitions", category=SkillCategory.BASE, value=0),
        Skill(name="Disguise", category=SkillCategory.BASE, value=0),
        Skill(name="Interrogation", category=SkillCategory.BASE, value=0),
        Skill(name="Lockpicking", category=SkillCategory.BASE, value=0),
        Skill(name="Mechanic", category=SkillCategory.BASE, value=0),
        Skill(name="Pickpocket", category=SkillCategory.BASE, value=0),
        Skill(name="Research", category=SkillCategory.BASE, value=0),
        Skill(name="Restoration", category=SkillCategory.BASE, value=0),
        Skill(name="Safecracking", category=SkillCategory.BASE, value=0),
        Skill(name="Traps", category=SkillCategory.BASE, value=0),

        # Knowledge skills (Botany is described in the rules but missing from
        # their summary)
        Skill(name="Anthropology", category=SkillCategory.BASE, value=0),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=0),
        Skill(name="Botany", category=SkillCategory.BASE, value=0),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=0),
        Skill(name="Civil Engineering", category=SkillCategory.BASE, value=0),
        Skill(name="Electrical Engineering", category=SkillCategory.BASE, value=0),
        Skill(name="Finance", category=SkillCategory.BASE, value=0),
        Skill(name="Forensic Science", category=SkillCategory.BASE, value=0),
        Skill(name="Geology", category=SkillCategory.BASE, value=0),
        Skill(name="History", category=SkillCategory.GENERIC, value=0),
        Skill(name="Language", category=SkillCategory.GENERIC, value=0),
        Skill(name="Law", category=SkillCategory.BASE, value=0),
        Skill(name="Linguistics", category=SkillCategory.BASE, value=0),
        Skill(name="Military Science", category=SkillCategory.BASE, value=0),
        Skill(name="Navigation", category=SkillCategory.BASE, value=0),
        Skill(name="Occult Studies", category=SkillCategory.BASE, value=0),
        Skill(name="Paleontology", category=SkillCategory.BASE, value=0),
        Skill(name="Physics", category=SkillCategory.BASE, value=0),
        Skill(name="Rhetoric", category=SkillCategory.BASE, value=0),
        Skill(name="Zoology", category=SkillCategory.BASE, value=0),
        # Medical skills (Advanced Medical needs a First Aid BCS of 5, the
        # others an Advanced Medical BCS of 5)
        Skill(name="First Aid", category=SkillCategory.BASE, value=0),
        Skill(name="Advanced Medical", category=SkillCategory.BASE, value=0),
        Skill(name="Pathology", category=SkillCategory.BASE, value=0),
        Skill(name="Therapy", category=SkillCategory.BASE, value=0),
        Skill(name="Medical Specialization", category=SkillCategory.GENERIC, value=0),

        # Culture skills
        Skill(name="Arabic Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Black African Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Chinese Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Eskimo Culture", category=SkillCategory.BASE, value=0),
        Skill(name="European/American Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Indian Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Japanese Culture", category=SkillCategory.BASE, value=0),
        Skill(name="North Amerindian Culture", category=SkillCategory.BASE, value=0),
        Skill(name="Polynesian Culture", category=SkillCategory.BASE, value=0),
        Skill(name="South Amerindian Culture", category=SkillCategory.BASE, value=0),

        # Sub-culture skills
        Skill(name="Academic Subculture", category=SkillCategory.BASE, value=0),
        Skill(name="Business Subculture", category=SkillCategory.BASE, value=0),
        Skill(name="Criminal Subculture", category=SkillCategory.BASE, value=0),
        Skill(name="Law Enforcement Subculture", category=SkillCategory.BASE, value=0),
        Skill(name="Politics Subculture", category=SkillCategory.BASE, value=0),
        Skill(name="High Society Subculture", category=SkillCategory.BASE, value=0),

        # Firearm skills
        Skill(name="Pistol", category=SkillCategory.BASE, value=0),
        Skill(name="Rifle", category=SkillCategory.BASE, value=0),
        Skill(name="Autofire", category=SkillCategory.BASE, value=0),

        # Armed combat skills
        Skill(name="Archaic Weapon", category=SkillCategory.GENERIC, value=0),
        Skill(name="Bayonet Training", category=SkillCategory.BASE, value=0),
        Skill(name="Fencing", category=SkillCategory.BASE, value=0),
        Skill(name="Knife", category=SkillCategory.BASE, value=0),
        Skill(name="Nightstick", category=SkillCategory.BASE, value=0),
        Skill(name="Whip", category=SkillCategory.BASE, value=0),

        # Unarmed combat skills
        Skill(name="Brawling", category=SkillCategory.BASE, value=0),
        Skill(name="Martial Arts", category=SkillCategory.BASE, value=0),
    ],
)
