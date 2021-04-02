import streamlit as st

from functools import reduce
from googleapi import google
from urllib.parse import unquote
import wikipedia

wikipedia.set_lang("ar")
import re
from transformers import AutoTokenizer, pipeline
from preprocess import ArabertPreprocessor


preprocessor = ArabertPreprocessor("wissamantoun/araelectra-base-artydiqa")
tokenizer = AutoTokenizer.from_pretrained("wissamantoun/araelectra-base-artydiqa")
qa_pipe = pipeline("question-answering", model="wissamantoun/araelectra-base-artydiqa")

def get_results(question):
    search_results = google.search(question + " site:ar.wikipedia.org")
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
                    print(f"Subsection found with length: {len(prep_subsection)}")
                sections.extend(subsections)
            else:
                print(f"Regular Section with length: {len(prep_section)}")
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
            print(
                f"full section length: {len(tokenizer.tokenize(preprocessor.preprocess(temp_section)))}"
            )
            temp_section = ""
        else:
            temp_section += " " + section + " "

    results = qa_pipe(
        question=[preprocessor.preprocess(question)] * len(full_len_sections),
        context=[preprocessor.preprocess(x) for x in full_len_sections],
    )

    sorted_results = sorted(results, reverse=True, key=lambda x: x['score'])

    return sorted_results[0:min(3,len(sorted_results))]
