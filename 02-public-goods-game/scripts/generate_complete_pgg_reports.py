#!/usr/bin/env python3
"""
scripts/generate_complete_pgg_reports.py
Comprehensive, publication-grade report generator for all PGG Peer-Swap Experiments.
Generates:
  1. PGG_Peer_Detection_Comprehensive_Report.docx
  2. pgg_peer_detection_comprehensive_report.html
"""

import base64
import os
import shutil
import sys
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs" / "pgg_swap"
FIGS_DIR = OUTPUTS_DIR / "figures"
DOCX_OUT = ROOT_DIR / "PGG_Peer_Detection_Comprehensive_Report.docx"
DOCX_COPY = OUTPUTS_DIR / "PGG_Peer_Detection_Comprehensive_Report.docx"
HTML_OUT = ROOT_DIR / "pgg_peer_detection_comprehensive_report.html"

# Helper for base64 encoding images
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Images dictionary
IMAGES = {}
for fig_file in FIGS_DIR.glob("*.png"):
    IMAGES[fig_file.name] = {
        "path": fig_file,
        "base64": get_base64_image(fig_file)
    }

print(f"Loaded {len(IMAGES)} images into memory.")

