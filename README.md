# gherkin-glossary-python


<div align="center">
    <h4>
        Parse .feature files to build a glossary of unique Gherkin terms
    </h4>
</div>

---

[![License: MIT](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/david-luison-starkey/bash-annotations/blob/main/LICENSE)

---

## Introduction

`gherkin-glossary` is a script that finds all `.feature` (or otherwise specified) files within a directory structure and 
creates a `json` file of unique `Gherkin` terms, grouped by keyword or type, including:

- Given
- When
- Then
- tags (anything prepended by @)
- comments (anything prepended by #)

Optional custom parameter type identification is also supported ([Cucumber documentation](https://cucumber.io/docs/cucumber/configuration/)), 
and can be provided to the script via a `json` file that matches 
[`schema.json`](https://github.com/david-luison-starkey/gherkin-glossary-python/blob/main/src/schema.json).

All instances of parameterised types, including `string`, `int`, and `data table` values are made generic in generating the glossary, to 
avoid unnecessary duplication of what is essentially the same statement.

## Usage

Run `python main.py --help` for a list of arguments and their help text.

The script is also capable of generating a `json` for the traversed directory structure which can be used as input to the 
script for subsequent runs.

Once generated, the glossary `json` could be used to generate documentation for technical and non-technical 
users alike (such as Confluence, using its REST API and 
[atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api)).

