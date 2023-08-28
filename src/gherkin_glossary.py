from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import chain

from gherkin_keywords import GherkinKeywords


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
        """
        Replaces 'And', 'But', and '*' with 'Given' or 'Then', depending
        on which keyword preceded the conjunction.

        Invoked on instantiation to provide an accurate glossary of terms.
        """
        statements_list = gherkin_statements.copy()
        for index, _ in enumerate(statements_list):
            replaced = self._keyword_lookbehind(index, statements_list)
            if replaced:
                statements_list = replaced
        return statements_list

    def _keyword_lookbehind(
        self, current_index: int, gherkin_statements: list[str]
    ) -> list[str] | None:
        # Iterates backward through list of gherkin statement to find
        # parent keyword that alias is representing. If found, that statement is
        # updated and a new list of gherkin statements is returned.

        statements_list = gherkin_statements.copy()
        current_statement = statements_list[current_index]
        conjunctions = GherkinKeywords.conjunctions()

        if current_statement.startswith(conjunctions):
            conjunction_to_replace = GherkinKeywords(
                self._get_gherkin_keyword_from_statement(current_statement)
            )

            x = current_index - 1
            while x >= 0:
                if statements_list[x].startswith(GherkinKeywords.aliasable()):
                    keyword = GherkinKeywords(
                        self._get_gherkin_keyword_from_statement(statements_list[x])
                    )
                    statements_list[current_index] = current_statement.replace(
                        conjunction_to_replace, keyword
                    )
                    return statements_list
                elif statements_list[x].startswith(GherkinKeywords.not_aliasable()):
                    raise ValueError(
                        f"\n\tGherkin syntax malformed. '{conjunction_to_replace}' "
                        f"in '{current_statement}' "
                        f"should be preceded by {GherkinKeywords.aliasable()}."
                        f"\n\tInstead is preceded by '{statements_list[x]}'."
                    )
                x = x - 1
                if x < 0:
                    raise ValueError(
                        "\n\tNo valid preceding statement found for "
                        f"'{current_statement}'."
                    )
        return None

    def _get_gherkin_keyword_from_statement(self, gherkin_statement: str) -> str:
        # Retrieve first word in statement, which is a keyword in gherkin syntax
        return gherkin_statement.split()[0]

    def get_gherkin_terms(self, keyword: GherkinKeywords) -> set[str]:
        """
        Returns a set of gherkin terms associated with the Gherkin keyword argument.

        Variables are replaced with their corresponding placeholder to prevent term
        duplication.
        """
        return {
            self._replace_custom_type_values_with_placeholder_types(
                self._replace_variables_with_placeholder_types(item)
            )
            for item in self.gherkin_statements
            if item.startswith(keyword)
        }

    def _replace_variables_with_placeholder_types(self, gherkin_statement: str) -> str:
        # Integers replaced with {int}, strings replaced with {string}, data table
        # references replaced with <data table>,
        data_table_type = re.sub(
            r"\"<[a-zA-Z\s0-9]+>\"", " <data table> ", gherkin_statement
        )
        int_type = re.sub(r"\s[0-9]+\s", " {int} ", data_table_type)
        string_type = re.sub(r"\"[a-zA-Z\s0-9]+\"", " {string} ", int_type)
        trimmed = re.sub(r"[\s]{2,}", " ", string_type).rstrip()
        return trimmed

    def _replace_custom_type_values_with_placeholder_types(
        self, gherkin_statement: str
    ) -> str:
        # Custom types replaced with {custom type name}.
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
        """
        Returns set of tags (ignored commented out tags)
        """
        return set(
            chain.from_iterable(
                {tag for tag in line.split() if tag.startswith("@") and "#" not in tag}
                for line in self.gherkin_statements
            )
        )

    def get_comments(self) -> set[str]:
        """
        Returns statements prepended with '#'
        """
        return {
            comment for comment in self.gherkin_statements if comment.startswith("#")
        }
