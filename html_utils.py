import os
import re

import streamlit as st
from htbuilder import (HtmlElement, a, br, classes, div, fonts, hr, img, li, p,
                       styles, ul)
from htbuilder.funcs import rgb, rgba
from htbuilder.units import percent, px


def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 10px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        # color="black",
        text_align="center",
        height="auto",
        opacity=1,
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2),
    )

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Made by: ",
        link("https://twitter.com/wissam_antoun", "@WissamAntoun"),
        br(),
        "AI Reader: ",
        link("https://github.com/aub-mind/arabert", "AraELECTRA"),
        br(),
        # link(
        #     "https://sites.aub.edu.lb/mindlab",
        #     image("https://sites.aub.edu.lb/mindlab/files/2019/10/logo.png"),
        # ),
    ]
    layout(*myargs)


def ga():
    code = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-VQH8C3F39G"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-VQH8C3F39G');
    </script>
    """

    a = os.path.dirname(st.__file__) + "/static/index.html"
    with open(a, "r") as f:
        data = f.read()
        if len(re.findall("G-", data)) == 0:
            with open(a, "w") as ff:
                newdata = re.sub("<head>", "<head>" + code, data)
                ff.write(newdata)
