import streamlit as st
from annotated_text import annotated_text
import arabic_reshaper
from bidi.algorithm import get_display
from utils import get_results
from html_utils import footer


def annotate_answer(answer, context):
    start_idx = context.find(answer)
    end_idx = start_idx + len(answer)
    annotated_text(context[:start_idx], (answer, "ANSWER", "#8ef"), context[end_idx:])


st.set_page_config(
        page_title="Arabic QA app",
        page_icon="📖",
        # layout="wide"
        )
footer()


st.markdown("""
<style>
p, div, input, label {
  text-align: right;
}
</style>
    """, unsafe_allow_html=True)


rtl = lambda w: get_display(f"{arabic_reshaper.reshape(w)}")

st.title("إسألني أي شئ")

question = st.text_input(
    "", value="ما هو نظام الحكم في لبنان؟"
)

run_query = st.button("أجب")
if run_query:
    # https://discuss.streamlit.io/t/showing-a-gif-while-st-spinner-runs/5084
    with st.spinner("... جاري البحث "):
        results = get_results(question)

    st.write("## :الأجوبة هي")
    for result in results:
        st.write(result['answer'])
        "**Relevance:** " , result['score']