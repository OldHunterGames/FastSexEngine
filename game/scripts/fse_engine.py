# -*- coding: <UTF-8> -*-
from random import *
import renpy.store as store
import renpy.exports as renpy


class FSEngine(object):

    def __init__(self, combatants):
        self.combatants = combatants
        self.hero = combatants[0]
        self.opponent = combatants[1]
        self.opponent.potential_size = 1
        self.round = 0

    def start(self):
        for combatant in self.combatants:
            combatant.form_reserve()
            combatant.shuffle_reserve()
            for i in range(combatant.potential_size):
                combatant.draw_card()
        self.opponent.action = self.opponent.potential.pop(0)

    def new_turn(self):
        for combatant in self.combatants:
            combatant.draw_card()
        self.opponent.action = self.opponent.potential.pop(0)

    def render_input(self, data):
        location_to_call = "user_turn"
        if "act" in data:
            self.hero.action = data[1]
            self.hero.potential.remove(data[1])
            location_to_call = "resolution_phase"

        return location_to_call

    def resolution(self):

        special_effects = {
            self.hero: [],
            self.opponent: []
        }

        for combatant in self.combatants:
            if combatant == self.hero:
                anti_combatant = self.opponent
            else:
                anti_combatant = self.hero
            if combatant.action.suit == "passion" or combatant.action.suit == "brutality":
                special_effects[combatant].append("backlash")
            if combatant.action.suit == "insolence" and anti_combatant.action.suit == "passion":
                special_effects[combatant].append("reverse")
            elif combatant.action.suit == "temptation" and anti_combatant.action.suit == "brutality":
                special_effects[combatant].append("reverse")

            if "reverse" in special_effects[combatant]:
                combatant.arousal += combatant.action.value
            else:
                anti_combatant.arousal += combatant.action.value
            if "backlash" in special_effects[combatant]:
                combatant.arousal += combatant.action.value

        if self.hero.arousal >= self.hero.arousal_threshold:
            if self.opponent.arousal > self.hero.arousal:
                location_to_call = "you_win"
            else:
                location_to_call = "game_over"
        elif self.opponent.arousal >= self.opponent.arousal_threshold:
            location_to_call = "you_win"
        else:
            location_to_call = "user_turn"

        self.new_turn()
        return location_to_call


class FSECombatant(object):

    def __init__(self, person):
        self.name = person.name
        self.role = person.fse_role
        self.avatar = person.avatar
        self.gender = person.gender
        self.implements = person.implements
        self.skills = person.skills
        self.arousal = 0
        self.arousal_threshold = 10
        self.potential_size = person.spirit
        self.reserve = []
        self.potential = []
        self.discard = []
        self.action = None
        self.form_reserve()

    def form_reserve(self):
        self.reserve = []
        for implement in self.implements:
            for suit in implement.suits:
                for level in range(self.skills[implement.skill]+1):
                    self.reserve.append(FSEAction(implement.get_descriptor(suit, level + 1)))

    def shuffle_reserve(self):
        self.reserve.extend(self.discard)
        self.discard = []
        shuffle(self.reserve)

    def draw_card(self):
        if len(self.reserve) <= 0:
            self.shuffle_reserve()
        self.potential.append(self.reserve.pop(0))


class FSEAction(object):

    def __init__(self, descriptor):
        self.name = descriptor["name"]
        self.value = descriptor["value"]
        self.suit = descriptor["suit"]
        self.implement = descriptor["implement"]


class Person(object):
    """
    This is a class for a base character, to be converted into any engine-specific combatant
    """
    def __init__(self, name, role):
        self.name = name
        self.avatar = "images/ava/huntsman.jpg"
        self.gender = "male"
        self.fse_role = role
        self.physique = 3
        self.agility = 3
        self.spirit = 3
        self.mind = 3
        self.skills = {
            "manual": 1,
            "oral": 1,
            "penetration": 1
        }
        self.implements = [SexImplement("Hands"), SexImplement("Butt"), SexImplement("Mouth")]

        if name == "Slave":
            self.avatar = "images/ava/slave.jpg"
            self.implements.append(SexImplement("Vagina"))
        else:
            self.implements.append(SexImplement("Penis"))


class SexImplement(object):

    def __init__(self, name):
        self.name = name
        self.picture = ""
        self.skill = None   # Can be "manual", "oral", "penetration" or None
        # Suits and names for actions. Usually each implement have two suits with name for action of each suit
        self.suits = {
            "insolence": "insolent act",
            "passion": "passionate act",
            "brutality": "brutal act",
            "temptation": "tempting act",
        }
        if name == "Hands":
            self.skill = "manual"
            self.suits = {
                "brutality": "brutal slap",
                "temptation": "tempting caress",
            }
        if name == "Penis":
            self.skill = "penetration"
            self.suits = {
                "passion": "passionate strokes",
                "brutality": "brutal fuck",
            }
        if name == "Mouth":
            self.skill = "oral"
            self.suits = {
                "insolence": "insolent lick",
                "passion": "passionate kiss",
                "brutality": "brutal bite",
                "temptation": "tempting slurp",
            }
        if name == "Butt":
            self.skill = "penetration"
            self.suits = {
                "insolence": "insolent twists",
                "temptation": "tempting motions",
            }
        if name == "Vagina":
            self.skill = "penetration"
            self.suits = {
                "insolence": "insolent sweeps",
                "passion": "passionate contractions",
            }

    def get_descriptor(self, suit, value):
        descriptor = {
            "name": "{} [{}]".format(self.suits[suit], value),
            "value": value,
            "suit": suit,
            "implement": self
        }
        return descriptor



