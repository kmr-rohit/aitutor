from enum import Enum


class SessionMode(str, Enum):
    concept_learn = "concept_learn"
    hld_practice = "hld_practice"
    language_deep_dive = "language_deep_dive"
    rapid_qa = "rapid_qa"
