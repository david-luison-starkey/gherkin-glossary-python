from enum import StrEnum
from typing import Literal


class GherkinKeywords(StrEnum):
    FEATURE = "Feature"
    RULE = "Rule"
    BACKGROUND = "Background"
    SCENARIO = "Scenario"
    SCENARIO_OUTLINE = "Scenario Outline"
    GIVEN = "Given"
    WHEN = "When"
    THEN = "Then"
    AND = "And"
    BUT = "But"
    ASTERISK = "*"

    @classmethod
    def conjunctions(
        cls,
    ) -> tuple[Literal[AND], Literal[BUT], Literal[ASTERISK],]:
        return (GherkinKeywords.AND, GherkinKeywords.BUT, GherkinKeywords.ASTERISK)

    @classmethod
    def aliasable(cls) -> tuple[Literal[GIVEN], Literal[THEN]]:
        return (GherkinKeywords.GIVEN, GherkinKeywords.THEN)

    @classmethod
    def not_aliasable(
        cls,
    ) -> tuple[
        Literal[FEATURE],
        Literal[RULE],
        Literal[BACKGROUND],
        Literal[SCENARIO],
        Literal[SCENARIO_OUTLINE],
        Literal[WHEN],
    ]:
        return (
            GherkinKeywords.FEATURE,
            GherkinKeywords.RULE,
            GherkinKeywords.BACKGROUND,
            GherkinKeywords.SCENARIO,
            GherkinKeywords.SCENARIO_OUTLINE,
            GherkinKeywords.WHEN,
        )
