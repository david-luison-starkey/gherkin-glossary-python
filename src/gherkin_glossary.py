from __future__ import annotations
from dataclasses import dataclass
import re
from gherkin_keywords import GherkinKeywords
from itertools import chain


@dataclass
class GherkinCustomTypes:
    custom_type: str
    type_values: list[str]


class GherkinTermGlossary:
    def __init__(
        self,
        gherkin_statements: list[str],
        custom_types: list[GherkinCustomTypes] | None,
    ):
        self.gherkin_statements = self.replace_conjunctions_with_keyword(
            gherkin_statements
        )
        self.custom_types = custom_types
        self.given = self.get_gherkin_terms(GherkinKeywords.GIVEN)
        self.when = self.get_gherkin_terms(GherkinKeywords.WHEN)
        self.then = self.get_gherkin_terms(GherkinKeywords.THEN)
        self.tags = self.get_tags()
        self.comments = self.get_comments()

    def replace_conjunctions_with_keyword(
        self, gherkin_statements: list[str]
    ) -> list[str]:
        statement_list = gherkin_statements
        for index, line in enumerate(statement_list):
            replaced = self._keyword_lookbehind(index, statement_list)
            if replaced:
                statement_list = replaced
        return statement_list

    def _keyword_lookbehind(
        self, current_index: int, gherkin_statements: list[str]
    ) -> list[str] | None:
        statements_list = gherkin_statements
        conjunctions = GherkinKeywords.conjunctions()

        if statements_list[current_index].startswith(conjunctions):
            conjunction_to_replace = GherkinKeywords(
                statements_list[current_index].split()[0]
            )

            x = current_index - 1
            while x >= 0:
                if statements_list[x].startswith(GherkinKeywords.aliasable()):
                    keyword = GherkinKeywords(statements_list[x].split()[0])
                    statements_list[current_index] = statements_list[
                        current_index
                    ].replace(conjunction_to_replace, keyword)
                    return statements_list
                elif statements_list[x].startswith(GherkinKeywords.not_aliasable()):
                    raise ValueError(
                        f"\n\tGherkin syntax malformed. '{conjunction_to_replace}' "
                        f"in '{statements_list[current_index]}' "
                        f"should be preceded by {GherkinKeywords.aliasable()}."
                        f"\n\tInstead is preceded by '{statements_list[x]}'."
                    )
                x = x - 1
                if x < 0:
                    raise ValueError(
                        "\n\tNo valid preceding statement found for "
                        f"'{statements_list[current_index]}'."
                    )
        return None

    def get_gherkin_terms(self, type: GherkinKeywords) -> set[str]:
        return {
            self.replace_custom_type_values_with_type(
                self.replace_variables_with_types(item)
            )
            for item in self.gherkin_statements
            if item.startswith(type)
        }

    def replace_variables_with_types(self, gherkin_statement: str) -> str:
        data_table_type = re.sub(
            r"\"<[a-zA-Z\s0-9]+>\"", " <data table> ", gherkin_statement
        )
        int_type = re.sub(r"\s[0-9]+\s", " {int} ", data_table_type)
        string_type = re.sub(r"\"[a-zA-Z\s0-9]+\"", " {string} ", int_type)
        trimmed = re.sub(r"[\s]{2,}", " ", string_type).rstrip()
        return trimmed

    def replace_custom_type_values_with_type(self, gherkin_statement: str) -> str:
        types_replaced = gherkin_statement
        if self.custom_types:
            for custom_type in self.custom_types:
                for type_value in custom_type.type_values:
                    types_replaced = re.sub(
                        f"{type_value}",
                        f" {{{custom_type.custom_type}}} ",
                        types_replaced,
                    )
        return re.sub(r"[\s]{2,}", " ", types_replaced).rstrip()

    def get_tags(self) -> set[str]:
        return set(
            chain.from_iterable(
                {tag for tag in line.split() if tag.startswith("@") and "#" not in tag}
                for line in self.gherkin_statements
            )
        )

    def get_comments(self) -> set[str]:
        return {
            comment for comment in self.gherkin_statements if comment.startswith("#")
        }
