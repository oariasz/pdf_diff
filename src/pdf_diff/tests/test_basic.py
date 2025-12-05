from __future__ import annotations

from pdf_diff.comparator import ParagraphComparator
from pdf_diff.utils import Paragraph, normalize_text


def make_para(page: int, idx: int, gidx: int, text: str) -> Paragraph:
    return Paragraph(
        page=page,
        index_in_page=idx,
        global_index=gidx,
        text=text,
        norm_text=normalize_text(text),
    )


def test_normalize_text_basic():
    assert normalize_text(" Hola   mundo \n\n") == "Hola mundo"


def test_compare_paragraphs_replace_insert_delete():
    comparator = ParagraphComparator()

    a = [
        make_para(1, 1, 1, "Alpha paragraph"),
        make_para(1, 2, 2, "Beta paragraph"),
        make_para(1, 3, 3, "Gamma paragraph"),
    ]

    b = [
        make_para(1, 1, 1, "Alpha paragraph"),
        make_para(1, 2, 2, "Beta changed paragraph"),
        make_para(1, 3, 3, "Delta paragraph"),
        make_para(1, 4, 4, "Gamma paragraph"),
    ]

    diffs = comparator.compare_paragraphs(a, b)

    kinds = [d.kind for d in diffs]
    assert "REPLACE" in kinds or "INSERT" in kinds or "DELETE" in kinds
