import html
import logging
import re

import pyarabic.araby as araby

ACCEPTED_MODELS = [
    "bert-base-arabertv01",
    "bert-base-arabert",
    "bert-base-arabertv02",
    "bert-base-arabertv2",
    "bert-large-arabertv02",
    "bert-large-arabertv2",
    "araelectra-base",
    "araelectra-base-discriminator",
    "araelectra-base-generator",
    "aragpt2-base",
    "aragpt2-medium",
    "aragpt2-large",
    "aragpt2-mega",
]

SEGMENTED_MODELS = [
    "bert-base-arabert",
    "bert-base-arabertv2",
    "bert-large-arabertv2",
]


class ArabertPreprocessor:
    """
    A Preprocessor class that cleans and preprocesses text for all models in the AraBERT repo.
    It also can unprocess the text ouput of the generated text

    Args:

        model_name (:obj:`str`): model name from the HuggingFace Models page without the aubmindlab tag. Defaults to "bert-base-arabertv02". Current accepted models are:

            - :obj:`"bert-base-arabertv01"`: No farasa segmentation.
            - :obj:`"bert-base-arabert"`: with farasa segmentation.
            - :obj:`"bert-base-arabertv02"`: No farasas egmentation.
            - :obj:`"bert-base-arabertv2"`: with farasa segmentation.
            - :obj:`"bert-large-arabertv02"`: No farasas egmentation.
            - :obj:`"bert-large-arabertv2"`: with farasa segmentation.
            - :obj:`"araelectra-base"`: No farasa segmentation.
            - :obj:`"araelectra-base-discriminator"`: No farasa segmentation.
            - :obj:`"araelectra-base-generator"`: No farasa segmentation.
            - :obj:`"aragpt2-base"`: No farasa segmentation.
            - :obj:`"aragpt2-medium"`: No farasa segmentation.
            - :obj:`"aragpt2-large"`: No farasa segmentation.
            - :obj:`"aragpt2-mega"`: No farasa segmentation.

        keep_emojis(:obj: `bool`): don't remove emojis while preprocessing. Defaults to False

        remove_html_markup(:obj: `bool`): Whether to remove html artfacts, should be set to False when preprocessing TyDi QA. Defaults to True

        replace_urls_emails_mentions(:obj: `bool`): Whether to replace email urls and mentions by special tokens. Defaults to True

        strip_tashkeel(:obj: `bool`): remove diacritics (FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN, SHADDA)

        strip_tatweel(:obj: `bool`): remove tatweel '\\u0640'

        insert_white_spaces(:obj: `bool`): insert whitespace before and after all non Arabic digits or English digits or Arabic and English Alphabet or the 2 brackets, then inserts whitespace between words and numbers or numbers and words

        remove_elongation(:obj: `bool`): replace repetition of more than 2 non-digit character with 2 of this character


    Returns:

        ArabertPreprocessor: the preprocessor class

    Example:

        from preprocess import ArabertPreprocessor

        arabert_prep = ArabertPreprocessor("aubmindlab/bert-base-arabertv2")

        arabert_prep.preprocess("SOME ARABIC TEXT")
    """

    def __init__(
        self,
        model_name,
        keep_emojis=False,
        remove_html_markup=True,
        replace_urls_emails_mentions=True,
        strip_tashkeel=True,
        strip_tatweel=True,
        insert_white_spaces=True,
        remove_elongation=True,
    ):
        """
        model_name (:obj:`str`): model name from the HuggingFace Models page without the aubmindlab tag. Defaults to "bert-base-arabertv02". Current accepted models are:

            - :obj:`"bert-base-arabertv01"`: No farasa segmentation.
            - :obj:`"bert-base-arabert"`: with farasa segmentation.
            - :obj:`"bert-base-arabertv02"`: No farasas egmentation.
            - :obj:`"bert-base-arabertv2"`: with farasa segmentation.
            - :obj:`"bert-large-arabertv02"`: No farasas egmentation.
            - :obj:`"bert-large-arabertv2"`: with farasa segmentation.
            - :obj:`"araelectra-base"`: No farasa segmentation.
            - :obj:`"araelectra-base-discriminator"`: No farasa segmentation.
            - :obj:`"araelectra-base-generator"`: No farasa segmentation.
            - :obj:`"aragpt2-base"`: No farasa segmentation.
            - :obj:`"aragpt2-medium"`: No farasa segmentation.
            - :obj:`"aragpt2-large"`: No farasa segmentation.
            - :obj:`"aragpt2-mega"`: No farasa segmentation.

        keep_emojis(:obj: `bool`): don't remove emojis while preprocessing. Defaults to False

        remove_html_markup(:obj: `bool`): Whether to remove html artfacts, should be set to False when preprocessing TyDi QA. Defaults to True

        replace_urls_emails_mentions(:obj: `bool`): Whether to replace email urls and mentions by special tokens. Defaults to True

        strip_tashkeel(:obj: `bool`): remove diacritics (FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SUKUN, SHADDA)

        strip_tatweel(:obj: `bool`): remove tatweel '\\u0640'

        insert_white_spaces(:obj: `bool`): insert whitespace before and after all non Arabic digits or English digits or Arabic and English Alphabet or the 2 brackets, then inserts whitespace between words and numbers or numbers and words

        remove_elongation(:obj: `bool`): replace repetition of more than 2 non-digit character with 2 of this character

        """
        model_name = model_name.replace("aubmindlab/", "")

        if model_name not in ACCEPTED_MODELS:
            logging.warning(
                "Model provided is not in the accepted model list. Assuming you don't want Farasa Segmentation"
            )
            self.model_name = "bert-base-arabertv02"
        else:
            self.model_name = model_name


        self.keep_emojis = keep_emojis

        self.remove_html_markup = remove_html_markup
        self.replace_urls_emails_mentions = replace_urls_emails_mentions
        self.strip_tashkeel = strip_tashkeel
        self.strip_tatweel = strip_tatweel
        self.insert_white_spaces = insert_white_spaces
        self.remove_elongation = remove_elongation

    def preprocess(self, text):
        """
        Preprocess takes an input text line an applies the same preprocessing used in AraBERT
                            pretraining

        Args:

            text (:obj:`str`): inout text string

        Returns:

            string: A preprocessed string depending on which model was selected
        """


        text = str(text)
        text = html.unescape(text)
        if self.strip_tashkeel:
            text = araby.strip_tashkeel(text)
        if self.strip_tatweel:
            text = araby.strip_tatweel(text)

        if self.replace_urls_emails_mentions:
            # replace all possible URLs
            for reg in url_regexes:
                text = re.sub(reg, " [رابط] ", text)
            # REplace Emails with [بريد]
            for reg in email_regexes:
                text = re.sub(reg, " [بريد] ", text)
            # replace mentions with [مستخدم]
            text = re.sub(user_mention_regex, " [مستخدم] ", text)

        if self.remove_html_markup:
            # remove html line breaks
            text = re.sub("<br />", " ", text)
            # remove html markup
            text = re.sub("</?[^>]+>", " ", text)

        # remove repeated characters >2
        if self.remove_elongation:
            text = self._remove_elongation(text)

        # insert whitespace before and after all non Arabic digits or English Digits and Alphabet and the 2 brackets
        if self.insert_white_spaces:
            text = re.sub(
                "([^0-9\u0621-\u063A\u0641-\u064A\u0660-\u0669a-zA-Z\[\]])",
                r" \1 ",
                text,
            )

            # insert whitespace between words and numbers or numbers and words
            text = re.sub(
                "(\d+)([\u0621-\u063A\u0641-\u064A\u0660-\u066C]+)", r" \1 \2 ", text
            )
            text = re.sub(
                "([\u0621-\u063A\u0641-\u064A\u0660-\u066C]+)(\d+)", r" \1 \2 ", text
            )


        text = re.sub(rejected_chars_regex, " ", text)

        # remove extra spaces
        text = " ".join(text.replace("\uFE0F", "").split())

        # ALl the other models dont require Farasa Segmentation
        return text

    def unpreprocess(self, text, desegment=True):
        """Re-formats the text to a classic format where punctuations, brackets, parenthesis are not seperated by whitespaces.
        The objective is to make the generated text of any model appear natural and not preprocessed.

        Args:
            text (str): input text to be un-preprocessed
            desegment (bool, optional): [whether or not to remove farasa pre-segmentation before]. Defaults to True.

        Returns:
            str: The unpreprocessed (and possibly Farasa-desegmented) text.
        """

        # removes the spaces around quotation marks ex: i " ate " an apple --> i "ate" an apple
        # https://stackoverflow.com/a/53436792/5381220
        text = re.sub(white_spaced_double_quotation_regex, '"' + r"\1" + '"', text)
        text = re.sub(white_spaced_single_quotation_regex, "'" + r"\1" + "'", text)
        text = re.sub(white_spaced_back_quotation_regex, "\`" + r"\1" + "\`", text)
        text = re.sub(white_spaced_back_quotation_regex, "\—" + r"\1" + "\—", text)

        # during generation, sometimes the models don't put a space after the dot, this handles it
        text = text.replace(".", " . ")
        text = " ".join(text.split())

        # handle decimals
        text = re.sub(r"(\d+) \. (\d+)", r"\1.\2", text)
        text = re.sub(r"(\d+) \, (\d+)", r"\1,\2", text)

        text = re.sub(left_and_right_spaced_chars, r"\1", text)
        text = re.sub(left_spaced_chars, r"\1", text)
        text = re.sub(right_spaced_chars, r"\1", text)

        return text


    def _remove_elongation(self, text):
        """
        :param text:  the input text to remove elongation
        :return: delongated text
        """
        # loop over the number of times the regex matched the text
        for index_ in range(len(re.findall(regex_tatweel, text))):
            elongation = re.search(regex_tatweel, text)
            if elongation:
                elongation_pattern = elongation.group()
                elongation_replacement = elongation_pattern[0]
                elongation_pattern = re.escape(elongation_pattern)
                text = re.sub(
                    elongation_pattern, elongation_replacement, text, flags=re.MULTILINE
                )
            else:
                break
        return text

    def _remove_redundant_punct(self, text):
        text_ = text
        result = re.search(redundant_punct_pattern, text)
        dif = 0
        while result:
            sub = result.group()
            sub = sorted(set(sub), key=sub.index)
            sub = " " + "".join(list(sub)) + " "
            text = "".join(
                (text[: result.span()[0] + dif], sub, text[result.span()[1] + dif :])
            )
            text_ = "".join(
                (text_[: result.span()[0]], text_[result.span()[1] :])
            ).strip()
            dif = abs(len(text) - len(text_))
            result = re.search(redundant_punct_pattern, text_)
        text = re.sub(r"\s+", " ", text)
        return text.strip()


prefix_list = [
    "ال",
    "و",
    "ف",
    "ب",
    "ك",
    "ل",
    "لل",
    "\u0627\u0644",
    "\u0648",
    "\u0641",
    "\u0628",
    "\u0643",
    "\u0644",
    "\u0644\u0644",
    "س",
]
suffix_list = [
    "ه",
    "ها",
    "ك",
    "ي",
    "هما",
    "كما",
    "نا",
    "كم",
    "هم",
    "هن",
    "كن",
    "ا",
    "ان",
    "ين",
    "ون",
    "وا",
    "ات",
    "ت",
    "ن",
    "ة",
    "\u0647",
    "\u0647\u0627",
    "\u0643",
    "\u064a",
    "\u0647\u0645\u0627",
    "\u0643\u0645\u0627",
    "\u0646\u0627",
    "\u0643\u0645",
    "\u0647\u0645",
    "\u0647\u0646",
    "\u0643\u0646",
    "\u0627",
    "\u0627\u0646",
    "\u064a\u0646",
    "\u0648\u0646",
    "\u0648\u0627",
    "\u0627\u062a",
    "\u062a",
    "\u0646",
    "\u0629",
]
other_tokens = ["[رابط]", "[مستخدم]", "[بريد]"]

# the never_split list is ussed with the transformers library
prefix_symbols = [x + "+" for x in prefix_list]
suffix_symblos = ["+" + x for x in suffix_list]
never_split_tokens = list(set(prefix_symbols + suffix_symblos + other_tokens))

url_regexes = [
    r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",
    r"@(https?|ftp)://(-\.)?([^\s/?\.#-]+\.?)+(/[^\s]*)?$@iS",
    r"http[s]?://[a-zA-Z0-9_\-./~\?=%&]+",
    r"www[a-zA-Z0-9_\-?=%&/.~]+",
    r"[a-zA-Z]+\.com",
    r"(?=http)[^\s]+",
    r"(?=www)[^\s]+",
    r"://",
]
user_mention_regex = r"@[\w\d]+"
email_regexes = [r"[\w-]+@([\w-]+\.)+[\w-]+", r"\S+@\S+"]
redundant_punct_pattern = (
    r"([!\"#\$%\'\(\)\*\+,\.:;\-<=·>?@\[\\\]\^_ـ`{\|}~—٪’،؟`୍“؛”ۚ【»؛\s+«–…‘]{2,})"
)
regex_tatweel = r"(\D)\1{2,}"
rejected_chars_regex = r"[^0-9\u0621-\u063A\u0640-\u066C\u0671-\u0674a-zA-Z\[\]!\"#\$%\'\(\)\*\+,\.:;\-<=·>?@\[\\\]\^_ـ`{\|}~—٪’،؟`୍“؛”ۚ»؛\s+«–…‘]"

regex_url_step1 = r"(?=http)[^\s]+"
regex_url_step2 = r"(?=www)[^\s]+"
regex_url = r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
regex_mention = r"@[\w\d]+"
regex_email = r"\S+@\S+"

chars_regex = r"0-9\u0621-\u063A\u0640-\u066C\u0671-\u0674a-zA-Z\[\]!\"#\$%\'\(\)\*\+,\.:;\-<=·>?@\[\\\]\^_ـ`{\|}~—٪’،؟`୍“؛”ۚ»؛\s+«–…‘"

white_spaced_double_quotation_regex = r'\"\s+([^"]+)\s+\"'
white_spaced_single_quotation_regex = r"\'\s+([^']+)\s+\'"
white_spaced_back_quotation_regex = r"\`\s+([^`]+)\s+\`"
white_spaced_em_dash = r"\—\s+([^—]+)\s+\—"

left_spaced_chars = r" ([\]!#\$%\),\.:;\?}٪’،؟”؛…»·])"
right_spaced_chars = r"([\[\(\{“«‘*\~]) "
left_and_right_spaced_chars = r" ([\+\-\<\=\>\@\\\^\_\|\–]) "
