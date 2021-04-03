from urllib.parse import unquote

import arabic_reshaper
import streamlit as st
from bidi.algorithm import get_display

# from html_utils import footer

from utils import annotate_answer, get_results, shorten_text

st.set_page_config(
    page_title="Arabic QA app",
    page_icon="📖",
    initial_sidebar_state="collapsed"
    # layout="wide"
)
# footer()


rtl = lambda w: get_display(f"{arabic_reshaper.reshape(w)}")


_, col1, _ = st.beta_columns(3)

with col1:
    st.image("is2alni_logo.png",width=200)
    st.title("إسألني أي شيء")

st.markdown(
    """
<style>
p, div, input, label {
  text-align: right;
}
</style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Info")

st.sidebar.write("Made by [Wissam Antoun](https://twitter.com/wissam_antoun)")
st.sidebar.write("Powered by [AraELECTRA](https://github.com/aub-mind/arabert)")

question = st.text_input("", value="ما هو نظام لبنان؟")
if "؟" not in question:
    question += "؟"

run_query = st.button("أجب")
if run_query:
    # https://discuss.streamlit.io/t/showing-a-gif-while-st-spinner-runs/5084
    with st.spinner("... جاري البحث "):
        results_dict = get_results(question)

    if len(results_dict) > 0:
        st.write("## :الأجوبة هي")
        for result in results_dict["results"]:
            annotate_answer(result)
            f"[**المصدر**](<{result['link']}>)"
    else:
        st.write("## ليس لدي جواب")
