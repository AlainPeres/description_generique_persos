"""
Generic Daredevils (FGU, 1982) character template.

Default values ("to be specified", 75 attribute points spread evenly, talents
and skill scores of 0) are meant to be replaced when describing an actual
character. Finances, degrees, military rank, criminal record, licenses and
contacts are described in `background`. Reputation is not modeled (its
rules are not in the rulebook).
"""

from models import Character, Attribute, AttributeCategory, Skill, SkillCategory
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
        Attribute(name="Wit", category=AttributeCategory.MAIN, value=13),
        Attribute(name="Will", category=AttributeCategory.MAIN, value=13),
        Attribute(name="Strength", category=AttributeCategory.MAIN, value=13),
        Attribute(name="Deftness", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Speed", category=AttributeCategory.MAIN, value=12),
        Attribute(name="Health", category=AttributeCategory.MAIN, value=12),

        # Talents (advanced rule), at most 20
        Attribute(name="Charismatic", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Combative", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Communicative", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Esthetic", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Mechanical", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Natural", category=AttributeCategory.TALENT, value=0),
        Attribute(name="Scientific", category=AttributeCategory.TALENT, value=0),

        # Initialized as (Wit + Will + Deftness) / 6, then improved on its own,
        # so it is stored
        Attribute(name="Off-hand Dexterity", category=AttributeCategory.SECONDARY, value=6),

        # Current damage, in points; critical damage is kept per location
        # in specific_values.critical_damage
        Attribute(name="Lethal Damage", category=AttributeCategory.STATE, value=0),
        Attribute(name="Subdual Damage", category=AttributeCategory.STATE, value=0),
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
        Skill(name="Acrobat", category=SkillCategory.BASE, value=0, base="Deftness + Speed + Natural"),
        Skill(name="Climbing", category=SkillCategory.BASE, value=0, base="Deftness + Strength + Natural"),
        Skill(name="Jumping", category=SkillCategory.BASE, value=0, base="Deftness + Strength + Natural"),
        Skill(name="Running", category=SkillCategory.BASE, value=0, base="Speed + Strength + Natural"),
        Skill(name="Swimming", category=SkillCategory.BASE, value=0, base="Speed + Strength + Natural"),
        Skill(name="Cyclist", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),   # motorcycles
        Skill(name="Driver", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Driver, Heavy Equipment", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Gambling", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Charismatic"),
        Skill(name="Horsemanship", category=SkillCategory.BASE, value=0, base="Will + Deftness + Natural"),
        Skill(name="Hunting", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Natural"),
        Skill(name="Mimicry", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Pilot", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Pilot, Aerostat", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Seamanship", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Natural"),
        Skill(name="Stealth", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Natural"),
        Skill(name="Survival", category=SkillCategory.BASE, value=0, base="Health + Wit + Natural"),
        Skill(name="Throwing", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Combative"),
        Skill(name="Tracking", category=SkillCategory.BASE, value=0, base="Wit + Natural + Natural"),

        # Task skills
        Skill(name="Blacksmith", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Carpenter", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Electrician", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Gunsmith", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Machinist", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Cryptography", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Esthetic"),
        Skill(name="Demolitions", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Disguise", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Charismatic"),
        Skill(name="Interrogation", category=SkillCategory.BASE, value=0, base="Wit + Will + Charismatic"),
        Skill(name="Lockpicking", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Mechanic", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Pickpocket", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Charismatic"),
        Skill(name="Research", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Communicative"),
        Skill(name="Restoration", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Esthetic"),
        Skill(name="Safecracking", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),
        Skill(name="Traps", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Mechanical"),

        # Knowledge skills (Botany is described in the rules but missing from
        # their summary)
        Skill(name="Anthropology", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Communicative"),
        Skill(name="Archaeology", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Mechanical"),
        Skill(name="Botany", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Natural"),
        Skill(name="Chemistry", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Mechanical"),
        Skill(name="Civil Engineering", category=SkillCategory.BASE, value=0, base="Wit + Mechanical + Scientific"),
        Skill(name="Electrical Engineering", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Mechanical"),
        Skill(name="Finance", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Charismatic"),
        Skill(name="Forensic Science", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Scientific"),
        Skill(name="Geology", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Natural"),
        Skill(name="History", category=SkillCategory.GENERIC, value=0, base="Wit + Natural + Scientific"),
        Skill(name="Language", category=SkillCategory.GENERIC, value=0, base="Wit + Communicative + Esthetic"),
        Skill(name="Law", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="Linguistics", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Scientific"),
        Skill(name="Military Science", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Combative"),
        Skill(name="Navigation", category=SkillCategory.BASE, value=0, base="Wit + Natural + Scientific"),
        Skill(name="Occult Studies", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Natural"),
        Skill(name="Paleontology", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Natural"),
        Skill(name="Physics", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Mechanical"),
        Skill(name="Rhetoric", category=SkillCategory.BASE, value=0, base="Will + Charismatic + Communicative"),
        Skill(name="Zoology", category=SkillCategory.BASE, value=0, base="Wit + Scientific + Natural"),
        # Medical skills (Advanced Medical needs a First Aid BCS of 5, the
        # others an Advanced Medical BCS of 5)
        Skill(name="First Aid", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Scientific"),
        Skill(name="Advanced Medical", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Scientific"),
        Skill(name="Pathology", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Scientific"),
        Skill(name="Therapy", category=SkillCategory.BASE, value=0, base="Wit + Deftness + Scientific"),
        Skill(name="Medical Specialization", category=SkillCategory.GENERIC, value=0, base="Wit + Scientific + Scientific"),

        # Culture skills
        Skill(name="Arabic Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Black African Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Chinese Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Eskimo Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="European/American Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Indian Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Japanese Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="North Amerindian Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="Polynesian Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),
        Skill(name="South Amerindian Culture", category=SkillCategory.BASE, value=0, base="Wit + Esthetic + Communicative"),

        # Sub-culture skills
        Skill(name="Academic Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="Business Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="Criminal Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="Law Enforcement Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="Politics Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),
        Skill(name="High Society Subculture", category=SkillCategory.BASE, value=0, base="Wit + Communicative + Charismatic"),

        # Firearm skills
        Skill(name="Pistol", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Combative"),
        Skill(name="Rifle", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Combative"),
        Skill(name="Autofire", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Combative"),

        # Armed combat skills
        Skill(name="Archaic Weapon", category=SkillCategory.GENERIC, value=0, base="Strength + Deftness + Combative"),
        Skill(name="Bayonet Training", category=SkillCategory.BASE, value=0, base="Strength + Deftness + Combative"),
        Skill(name="Fencing", category=SkillCategory.BASE, value=0, base="Speed + Deftness + Combative"),
        Skill(name="Knife", category=SkillCategory.BASE, value=0, base="Deftness + Speed + Combative"),
        Skill(name="Nightstick", category=SkillCategory.BASE, value=0, base="Strength + Deftness + Combative"),
        Skill(name="Whip", category=SkillCategory.BASE, value=0, base="Deftness + Wit + Combative"),

        # Unarmed combat skills
        Skill(name="Brawling", category=SkillCategory.BASE, value=0, base="Strength + Deftness + Combative"),
        Skill(name="Martial Arts", category=SkillCategory.BASE, value=0, base="Deftness + Speed + Combative"),
    ],
)
