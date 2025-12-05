#!/usr/bin/env python3
"""
CLI entrypoint para pdf_diff.

Uso:
    python pdf_diff.py file1.pdf file2.pdf [--output report.txt] [--json report.json]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pdf_diff.loader import PDFLoader
from pdf_diff.comparator import ParagraphComparator
from pdf_diff.reporter import DiffReport
from pdf_diff.utils import configure_logging


class CLIApp:
    """Orquestador principal del flujo CLI."""

    def __init__(self) -> None:
        self.loader = PDFLoader()
        self.comparator = ParagraphComparator()
        self.reporter = DiffReport()

    def run(self, file_a: Path, file_b: Path, output: Path | None, json_path: Path | None) -> int:
        """Ejecuta la comparación de los dos PDFs y genera reportes."""
        logging.info("Cargando PDF A: %s", file_a)
        doc_a = self.loader.load(file_a)

        logging.info("Cargando PDF B: %s", file_b)
        doc_b = self.loader.load(file_b)

        logging.info("Comparando imágenes por página")
        image_diffs = self.comparator.compare_images(doc_a, doc_b)

        logging.info("Comparando párrafos")
        text_diffs = self.comparator.compare_paragraphs(doc_a.paragraphs, doc_b.paragraphs)

        report = self.reporter.build_report(
            file_a=file_a,
            file_b=file_b,
            image_diffs=image_diffs,
            text_diffs=text_diffs,
        )

        # Salida a consola
        print(report.to_text())

        # Guardar reporte de texto
        if output:
            output.write_text(report.to_text(), encoding="utf-8")
            logging.info("Reporte de texto guardado en: %s", output)

        # Guardar reporte JSON
        if json_path:
            json_path.write_text(report.to_json(), encoding="utf-8")
            logging.info("Reporte JSON guardado en: %s", json_path)

        return 0


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos del CLI."""
    parser = argparse.ArgumentParser(
        prog="pdf_diff",
        description="Compara dos PDFs a nivel de texto (por párrafos) y presencia de imágenes.",
    )

    parser.add_argument("file1", type=str, help="Ruta del primer PDF.")
    parser.add_argument("file2", type=str, help="Ruta del segundo PDF.")

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Ruta opcional para guardar el reporte en texto.",
    )
    parser.add_argument(
        "--json",
        type=str,
        default=None,
        help="Ruta opcional para guardar el reporte en formato JSON.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nivel de logging.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal."""
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)

    file_a = Path(args.file1).expanduser().resolve()
    file_b = Path(args.file2).expanduser().resolve()

    if not file_a.exists() or not file_a.is_file():
        logging.error("No existe el archivo: %s", file_a)
        return 2
    if not file_b.exists() or not file_b.is_file():
        logging.error("No existe el archivo: %s", file_b)
        return 2

    output = Path(args.output).expanduser().resolve() if args.output else None
    json_path = Path(args.json).expanduser().resolve() if args.json else None

    app = CLIApp()
    try:
        return app.run(file_a, file_b, output, json_path)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Error inesperado ejecutando pdf_diff: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
