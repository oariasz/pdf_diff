from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Paragraph:
    """Representa un párrafo con metadatos de ubicación."""
    page: int                 # Página 1-based
    index_in_page: int        # Índice 1-based dentro de la página
    global_index: int         # Índice 1-based global en el documento
    text: str                 # Texto original del párrafo
    norm_text: str            # Texto normalizado


@dataclass(frozen=True)
class PDFDocument:
    """Modelo interno del PDF extraído."""
    path: str
    pages_text: list[str]
    paragraphs: list[Paragraph]
    images_per_page: list[int]   # Cantidad de imágenes detectadas por página


@dataclass(frozen=True)
class ImageDiff:
    """Diferencia de imágenes por página."""
    page: int
    images_a: int
    images_b: int


@dataclass(frozen=True)
class TextDiff:
    """Diferencia de texto entre párrafos alineados."""
    kind: str  # REPLACE | INSERT | DELETE
    a: Paragraph | None
    b: Paragraph | None
    similarity: float
    description: str


def configure_logging(level: str) -> None:
    """Configura logging global."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


_whitespace_re = re.compile(r"\s+", re.UNICODE)


def normalize_text(text: str) -> str:
    """Normaliza espacios para comparar texto de forma estable."""
    text = text.replace("\u00a0", " ")  # Espacio no separable
    return _whitespace_re.sub(" ", text).strip()


def split_into_paragraphs(page_text: str) -> list[str]:
    """
    Divide el texto de una página en párrafos.

    Heurística:
    - Separa por líneas en blanco.
    - Reduce ruido de saltos de línea.
    """
    if not page_text:
        return []

    # Normalizar saltos de línea a '\n'
    cleaned = page_text.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Separación por bloques vacíos
    blocks = re.split(r"\n\s*\n+", cleaned)

    paragraphs: list[str] = []
    for block in blocks:
        # Unir líneas internas del bloque para aproximar párrafo real
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        paragraph = " ".join(lines).strip()
        if paragraph:
            paragraphs.append(paragraph)

    return paragraphs


def safe_iter(items: Iterable) -> list:
    """Convierte iterables a lista de forma segura."""
    return list(items)
