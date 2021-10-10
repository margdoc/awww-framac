import os
import re

from . import models


def framac_function(file: str, flags: str) -> str:
    return os.popen(f"frama-c {flags} {file}").read()


def program_elements(file: str) -> str:
    return framac_function(file, "-wp -wp-print")


def result_file(file_pk: int) -> str:
    return f"results/{file_pk}.txt"


def result(file: str, file_pk: int) -> str:
    return framac_function(file, f"-wp -wp-log=\"r:{result_file(file_pk)}\"")


def verification(file: str, file_pk: int, prover: str, props: [str], rte: bool = False) -> str:
    props = f"-wp-prop=\"{props}\"" if len(props) > 0 else ""
    rte = "-wp-rte" if rte else ""

    return framac_function(file, f"-wp -wp-prover {prover} {props} {rte} -wp-log=\"r:{result_file(file_pk)}\"")


def get_result(file_pk: int) -> str:
    return os.popen(f"cat {result_file(file_pk)}").read()


goal_regex = f"(Goal .+ \(file .+, line (\d+)\).*:\n(?:.+\n)*Prover .+ returns (\w+)(?: .*)?\n(?:.+\n)*)"

section_regex = "@\s+([a-z]+(?: [a-z]+)?)"
sections = {
    "requires":         models.SectionCategory.Precondition,
    "ensures":          models.SectionCategory.PostCondition,
    "assert":           models.SectionCategory.Assertion,
    "lemma":            models.SectionCategory.Lemma,
    "loop invariant":   models.SectionCategory.Invariant,
    "procedure":        models.SectionCategory.Procedure,
    "property":         models.SectionCategory.Property
}


def parse_file(file_pk: int):
    file = models.File.objects.get(pk=file_pk)

    with file.content.open(mode="r") as content:
        code = content.readlines()

    searches = [
        re.findall(section_regex, code_line)
        for code_line in code
    ]

    searches = [
        (line_number + 1, search[0])
        for line_number, search in enumerate(searches)
        if len(search) > 0
    ]

    sections_categories = []

    for (line_number, category) in searches:
        for key in sections.keys():
            if key in category:
                sections_categories.append((line_number, sections[key]))

    return sections_categories


def generate_output(file_pk: int):
    file = models.File.objects.get(pk=file_pk)
    output = program_elements(file.content.path)

    return re.findall(goal_regex, output)


def parse_output(file_pk: int):
    output = generate_output(file_pk)
    return output


statuses = {
    "Valid":            models.SectionStatus.Proved,
    "Unknown":          models.SectionStatus.Unchecked,
    "Failed":           models.SectionStatus.Invalid,
    "CounterExample":   models.SectionStatus.CounterExample
}


def get_output(file_pk: int):
    sections = models.FileSection.objects.filter(file__id=file_pk).order_by("line")

    to_show = [
        (section.statusData.status, statuses[section.status], section.category)
        for section in sections
        if section.statusData is not None
    ]

    return to_show
