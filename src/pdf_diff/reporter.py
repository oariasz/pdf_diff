from __future__ import annotations

import logging
from difflib import SequenceMatcher
from typing import List

from .utils import ImageDiff, Paragraph, TextDiff, normalize_text


class ParagraphComparator:
    """
    Responsable de comparar:
    - Párrafos de dos documentos
    - Presencia de imágenes por página
    """

    def compare_images(self, doc_a, doc_b) -> list[ImageDiff]:
        """Compara el conteo de imágenes por página."""
        max_pages = max(len(doc_a.images_per_page), len(doc_b.images_per_page))
        diffs: list[ImageDiff] = []

        for i in range(max_pages):
            a_count = doc_a.images_per_page[i] if i < len(doc_a.images_per_page) else 0
            b_count = doc_b.images_per_page[i] if i < len(doc_b.images_per_page) else 0

            if a_count != b_count:
                diffs.append(ImageDiff(page=i + 1, images_a=a_count, images_b=b_count))

        return diffs

    def compare_paragraphs(self, paras_a: List[Paragraph], paras_b: List[Paragraph]) -> list[TextDiff]:
        """
        Compara dos listas globales de párrafos.

        Se usa SequenceMatcher sobre textos normalizados para:
        - Detectar reemplazos, inserciones y eliminaciones.
        - Permitir resincronización de forma natural.
        """
        a_keys = [p.norm_text for p in paras_a]
        b_keys = [p.norm_text for p in paras_b]

        # Si hay muchos párrafos idénticos vacíos, esto ayuda a estabilidad
        a_keys = [normalize_text(k) for k in a_keys]
        b_keys = [normalize_text(k) for k in b_keys]

        matcher = SequenceMatcher(a=a_keys, b=b_keys, autojunk=False)

        diffs: list[TextDiff] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            if tag == "replace":
                diffs.extend(self._handle_replace(paras_a, paras_b, i1, i2, j1, j2))
            elif tag == "delete":
                diffs.extend(self._handle_delete(paras_a, i1, i2))
            elif tag == "insert":
                diffs.extend(self._handle_insert(paras_b, j1, j2))

        logging.debug("Total diferencias de texto detectadas: %s", len(diffs))
        return diffs

    def _handle_replace(
        self,
        paras_a: List[Paragraph],
        paras_b: List[Paragraph],
        i1: int,
        i2: int,
        j1: int,
        j2: int,
    ) -> list[TextDiff]:
        """Gestiona bloques reemplazados."""
        block_a = paras_a[i1:i2]
        block_b = paras_b[j1:j2]

        diffs: list[TextDiff] = []

        # Alineación interna simple 1-1 hasta el largo mínimo
        min_len = min(len(block_a), len(block_b))

        for k in range(min_len):
            a_p = block_a[k]
            b_p = block_b[k]
            sim = SequenceMatcher(None, a_p.norm_text, b_p.norm_text).ratio()
            desc = self._describe_replace(sim)
            diffs.append(
                TextDiff(
                    kind="REPLACE",
                    a=a_p,
                    b=b_p,
                    similarity=sim,
                    description=desc,
                )
            )

        # Exceso en A -> deletes
        for a_p in block_a[min_len:]:
            diffs.append(
                TextDiff(
                    kind="DELETE",
                    a=a_p,
                    b=None,
                    similarity=0.0,
                    description="Párrafo presente en A pero ausente en B.",
                )
            )

        # Exceso en B -> inserts
        for b_p in block_b[min_len:]:
            diffs.append(
                TextDiff(
                    kind="INSERT",
                    a=None,
                    b=b_p,
                    similarity=0.0,
                    description="Párrafo presente en B pero ausente en A.",
                )
            )

        return diffs

    def _handle_delete(self, paras_a: List[Paragraph], i1: int, i2: int) -> list[TextDiff]:
        """Gestiona párrafos eliminados."""
        diffs: list[TextDiff] = []
        for a_p in paras_a[i1:i2]:
            diffs.append(
                TextDiff(
                    kind="DELETE",
                    a=a_p,
                    b=None,
                    similarity=0.0,
                    description="Párrafo presente en A pero ausente en B.",
                )
            )
        return diffs

    def _handle_insert(self, paras_b: List[Paragraph], j1: int, j2: int) -> list[TextDiff]:
        """Gestiona párrafos insertados."""
        diffs: list[TextDiff] = []
        for b_p in paras_b[j1:j2]:
            diffs.append(
                TextDiff(
                    kind="INSERT",
                    a=None,
                    b=b_p,
                    similarity=0.0,
                    description="Párrafo presente en B pero ausente en A.",
                )
            )
        return diffs

    def _describe_replace(self, similarity: float) -> str:
        """Genera una descripción breve según nivel de similitud."""
        if similarity >= 0.85:
            return "El texto difiere levemente entre ambos párrafos."
        if similarity >= 0.60:
            return "El texto difiere parcialmente entre ambos párrafos."
        return "El texto es considerablemente diferente entre ambos párrafos."
