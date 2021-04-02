import logging
import re
from functools import reduce
from urllib.parse import unquote

import streamlit as st
import wikipedia
from fuzzysearch import find_near_matches
from googleapi import google
from transformers import AutoTokenizer, pipeline

from annotator import annotated_text
from preprocess import ArabertPreprocessor

logger = logging.getLogger(__name__)

wikipedia.set_lang("ar")

preprocessor = ArabertPreprocessor("wissamantoun/araelectra-base-artydiqa")
tokenizer = AutoTokenizer.from_pretrained("wissamantoun/araelectra-base-artydiqa")
qa_pipe = pipeline("question-answering", model="wissamantoun/araelectra-base-artydiqa")


def get_results(question):
    search_results = google.search(
        question + " site:ar.wikipedia.org", lang="ar", area="ar"
    )
    if len(search_results) == 0:
        return {}
    page_name = search_results[0].link.split("wiki/")[-1]
    wiki_page = wikipedia.page(unquote(page_name))
    wiki_page_content = wiki_page.content

    sections = []
    for section in re.split("== .+ ==[^=]", wiki_page_content):
        if not section.isspace():
            prep_section = tokenizer.tokenize(preprocessor.preprocess(section))
            if len(prep_section) > 500:
                subsections = []
                for subsection in re.split("=== .+ ===", section):
                    if subsection.isspace():
                        continue
                    prep_subsection = tokenizer.tokenize(
                        preprocessor.preprocess(subsection)
                    )
                    subsections.append(subsection)
                    logger.info(f"Subsection found with length: {len(prep_subsection)}")
                sections.extend(subsections)
            else:
                logger.info(f"Regular Section with length: {len(prep_section)}")
                sections.append(section)

    full_len_sections = []
    temp_section = ""
    for section in sections:
        if (
            len(tokenizer.tokenize(preprocessor.preprocess(temp_section)))
            + len(tokenizer.tokenize(preprocessor.preprocess(section)))
            > 384
        ):
            if temp_section == "":
                temp_section = section
                continue
            full_len_sections.append(temp_section)
            logger.info(
                f"full section length: {len(tokenizer.tokenize(preprocessor.preprocess(temp_section)))}"
            )
            temp_section = ""
        else:
            temp_section += " " + section + " "
    if temp_section != "":
        full_len_sections.append(temp_section)

    results = qa_pipe(
        question=[preprocessor.preprocess(question)] * len(full_len_sections),
        context=[preprocessor.preprocess(x) for x in full_len_sections],
    )

    if not isinstance(results, list):
        results = [results]

    for result, section in zip(results, full_len_sections):
        result["original"] = section
        answer_match = find_near_matches(
            " " + preprocessor.unpreprocess(result["answer"]) + " ",
            result["original"],
            max_l_dist=min(5, len(preprocessor.unpreprocess(result["answer"])) // 2),
            max_deletions=0,
        )
        result["new_start"] = answer_match[0].start
        result["new_end"] = answer_match[0].end
        result["new_answer"] = answer_match[0].matched
        result["link"] = (
            search_results[0].link + "#:~:text=" + result["new_answer"].strip()
        )

    sorted_results = sorted(results, reverse=True, key=lambda x: x["score"])

    return_dict = {}
    return_dict["title"] = unquote(page_name)
    return_dict["results"] = sorted_results[0 : min(3, len(sorted_results))]

    logger.info(str(return_dict))

    return return_dict


def shorten_text(text, n, reverse=False):
    if reverse:
        text = text[::-1]
    words = iter(text.split())
    lines, current = [], next(words)
    for word in words:
        if len(current) + 1 + len(word) > n:
            break
            lines.append(current)
            current = word
        else:
            current += " " + word
    lines.append(current)
    if reverse:
        return lines[0][::-1]
    return lines[0]


def annotate_answer(result):
    annotated_text(
        shorten_text(
            result["original"][: result["new_start"]],
            500,
            reverse=True,
        ),
        (result["new_answer"], "جواب", "#8ef"),
        shorten_text(result["original"][result["new_end"] :], 500) + " ...... إلخ",
    )
