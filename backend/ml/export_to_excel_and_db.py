"""Export Digital Guardrails hybrid dataset to Excel (.xlsx) and seed SQLite database.
Benchmarks query speed: Indexed SQL database queries vs. Raw JSON disk parsing.
"""
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import time
from pathlib import Path
from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from sqlalchemy import select, func
from backend.database import engine, Base, SessionLocal, DatasetRecord

DATASET_JSON_PATH = Path('backend/ml/dataset.json')
DATASET_EXCEL_PATH = Path('backend/ml/dataset.xlsx')

def create_styled_excel(data):
    """Build a professional, multi-sheet Excel workbook from dataset.json."""
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styling definitions
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Navy Blue
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    accent_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid") # Light Blue
    accent_font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
    bold_font = Font(name="Calibri", size=11, bold=True)
    title_font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    regular_font = Font(name="Calibri", size=10)
    thin_border_side = Side(border_style="thin", color="CBD5E1")
    thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    thick_bottom = Border(bottom=Side(border_style="medium", color="1E3A8A"))

    # =========================================================================
    # SHEET 1: All Conversations (790 rows)
    # =========================================================================
    ws_conv = wb.create_sheet(title="All Conversations (790)")
    ws_conv.views.sheetView[0].showGridLines = True
    
    headers = [
        "Conversation ID", "Origin", "Source Dataset", "Language", "Script",
        "Pattern Label", "Risk Level", "Target Message", "Window Context (Multi-Turn)",
        "Turns Count", "Explainability Rationale"
    ]
    ws_conv.append(headers)

    for col_idx in range(1, len(headers) + 1):
        cell = ws_conv.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

    for r_idx, item in enumerate(data, start=2):
        row_values = [
            item.get("conversation_id", ""),
            item.get("origin", "synthetic").upper(),
            item.get("source_dataset", ""),
            item.get("language", ""),
            item.get("script", ""),
            item.get("pattern_label", ""),
            item.get("risk_level", ""),
            item.get("target_text", ""),
            item.get("window_text", ""),
            len(item.get("turns", [])),
            item.get("rationale") or ""
        ]
        ws_conv.append(row_values)
        
        # Format alternating row shading
        bg_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid") if r_idx % 2 == 0 else PatternFill(fill_type=None)
        for col_idx in range(1, len(headers) + 1):
            c = ws_conv.cell(row=r_idx, column=col_idx)
            c.font = regular_font
            c.border = thin_border
            if bg_fill.fill_type:
                c.fill = bg_fill
            if col_idx in [8, 9, 11]:  # Wrap text for dialogue and rationales
                c.alignment = Alignment(vertical="top", wrap_text=True)
            elif col_idx in [2, 4, 5, 6, 7, 10]:
                c.alignment = Alignment(horizontal="center", vertical="top")
            else:
                c.alignment = Alignment(vertical="top")

    # Auto-adjust column widths
    column_widths = {
        1: 20, # ID
        2: 12, # Origin
        3: 25, # Source
        4: 14, # Language
        5: 12, # Script
        6: 28, # Pattern Label
        7: 12, # Risk Level
        8: 45, # Target Text
        9: 55, # Window Text
        10: 12,# Turns Count
        11: 45 # Rationale
    }
    for col_idx, width in column_widths.items():
        col_letter = get_column_letter(col_idx)
        ws_conv.column_dimensions[col_letter].width = width

    ws_conv.freeze_panes = "A2"
    ws_conv.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(data) + 1}"

    # =========================================================================
    # SHEET 2: Dataset Summary & Data Card
    # =========================================================================
    ws_sum = wb.create_sheet(title="Dataset Summary", index=0)
    ws_sum.views.sheetView[0].showGridLines = True

    ws_sum["A1"] = "Digital Guardrails (Bal Suraksha) — Unified Child Safety Dataset Card"
    ws_sum["A1"].font = title_font
    ws_sum.merge_cells("A1:E1")

    ws_sum["A3"] = "Total Conversations:"
    ws_sum["B3"] = len(data)
    ws_sum["A3"].font = bold_font
    ws_sum["B3"].font = bold_font

    ws_sum["A4"] = "Neutral Class Ratio:"
    neutral_count = sum(1 for d in data if d["pattern_label"] == "neutral")
    ws_sum["B4"] = f"{(neutral_count / len(data)) * 100:.2f}% ({neutral_count}/{len(data)})"
    ws_sum["A4"].font = bold_font

    ws_sum["A5"] = "Harmful Threat Categories:"
    ws_sum["B5"] = f"{len(data) - neutral_count} ({((len(data) - neutral_count)/len(data))*100:.2f}%)"
    ws_sum["A5"].font = bold_font

    # Breakdown by Origin
    ws_sum["A7"] = "DATASET ORIGIN BREAKDOWN"
    ws_sum["A7"].font = accent_font
    ws_sum.merge_cells("A7:C7")
    for cell in ws_sum["A7:C7"][0]:
        cell.fill = accent_fill

    origin_headers = ["Origin Type", "Conversations", "Share (%)"]
    ws_sum.append(origin_headers)
    for col in range(1, 4):
        ws_sum.cell(row=8, column=col).font = bold_font
        ws_sum.cell(row=8, column=col).border = thick_bottom

    origin_counts = Counter(d.get("origin", "synthetic") for d in data)
    for orig, count in origin_counts.items():
        ws_sum.append([orig.upper(), count, f"{(count/len(data))*100:.2f}%"])

    # Breakdown by Pattern
    start_r = ws_sum.max_row + 2
    ws_sum.cell(row=start_r, column=1, value="RISK PATTERN DISTRIBUTION").font = accent_font
    ws_sum.merge_cells(f"A{start_r}:C{start_r}")
    for cell in ws_sum[f"A{start_r}:C{start_r}"][0]:
        cell.fill = accent_fill

    pattern_headers = ["Pattern Label", "Conversations", "Risk Level"]
    ws_sum.append(pattern_headers)
    for col in range(1, 4):
        ws_sum.cell(row=start_r+1, column=col).font = bold_font
        ws_sum.cell(row=start_r+1, column=col).border = thick_bottom

    pattern_counts = Counter(d["pattern_label"] for d in data)
    pattern_risk_map = {
        'neutral': 'Low (0)',
        'grooming_trust_building': 'Medium (60)',
        'grooming_isolation_request': 'Medium (66) -> High (80)',
        'grooming_coercive_language': 'High (78)',
        'bullying_harassment': 'High (72)'
    }
    for pat, count in pattern_counts.most_common():
        ws_sum.append([pat, count, pattern_risk_map.get(pat, 'Medium')])

    # Research Sources & Citations
    start_src = ws_sum.max_row + 2
    ws_sum.cell(row=start_src, column=1, value="RESEARCH SOURCE CITATIONS & LICENSES").font = accent_font
    ws_sum.merge_cells(f"A{start_src}:D{start_src}")
    for cell in ws_sum[f"A{start_src}:D{start_src}"][0]:
        cell.fill = accent_fill

    src_headers = ["Source Dataset", "Origin", "License / Access Terms", "Description & Academic Citation"]
    ws_sum.append(src_headers)
    for col in range(1, 5):
        ws_sum.cell(row=start_src+1, column=col).font = bold_font
        ws_sum.cell(row=start_src+1, column=col).border = thick_bottom

    citations = [
        ("HASOC 2020 Hindi", "Real", "Research / Academic Use (FIRE 2020)", "Mandl et al., FIRE 2020 track on Hate Speech and Offensive Content in Indo-European Languages."),
        ("BullyExplain", "Real", "MIT License (HuggingFace)", "Bharti et al., 2022. Multi-turn cyberbullying dataset with annotated explainability rationales."),
        ("DravidianLangTech", "Real", "Creative Commons CC-BY 4.0", "Chakravarthi et al., DravidianLangTech 2021 Offensive Language Identification in Dravidian Languages."),
        ("COMI-LINGUA", "Real", "Research / Non-Commercial", "Aggarwal et al., 2020. Clean Hindi-English code-mixed non-toxic conversation dialogues."),
        ("PAN12 Academic Reference", "Synthetic", "Academic Structural Reference Only", "Inches & Crestani, 2012. Overview of the 1st Author Profiling Task at PAN (Grooming Stage Pattern).")
    ]
    for src, orig, lic, desc in citations:
        ws_sum.append([src, orig, lic, desc])

    ws_sum.column_dimensions["A"].width = 30
    ws_sum.column_dimensions["B"].width = 18
    ws_sum.column_dimensions["C"].width = 30
    ws_sum.column_dimensions["D"].width = 65

    # =========================================================================
    # SHEET 3: Language Cross-Tabulation
    # =========================================================================
    ws_lang = wb.create_sheet(title="Language Matrix")
    ws_lang.views.sheetView[0].showGridLines = True

    ws_lang["A1"] = "CROSS-TABULATION: LANGUAGE VS RISK PATTERN"
    ws_lang["A1"].font = title_font
    ws_lang.merge_cells("A1:G1")

    patterns = sorted(list(set(d["pattern_label"] for d in data)))
    languages = sorted(list(set(d["language"] for d in data)))
    
    matrix_headers = ["Language"] + patterns + ["Total"]
    ws_lang.append(matrix_headers)
    for col in range(1, len(matrix_headers) + 1):
        cell = ws_lang.cell(row=3, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for lang in languages:
        row = [lang]
        total = 0
        for pat in patterns:
            cnt = sum(1 for d in data if d["language"] == lang and d["pattern_label"] == pat)
            row.append(cnt)
            total += cnt
        row.append(total)
        ws_lang.append(row)

    # Add totals row
    total_row = ["Total"]
    for pat in patterns:
        total_row.append(sum(1 for d in data if d["pattern_label"] == pat))
    total_row.append(len(data))
    ws_lang.append(total_row)

    # Style matrix cells
    for r in range(4, ws_lang.max_row + 1):
        is_total = (r == ws_lang.max_row)
        for c in range(1, len(matrix_headers) + 1):
            cell = ws_lang.cell(row=r, column=c)
            cell.border = thin_border
            if is_total:
                cell.font = bold_font
                cell.fill = accent_fill
            elif c == 1:
                cell.font = bold_font

    for col in range(1, len(matrix_headers) + 1):
        ws_lang.column_dimensions[get_column_letter(col)].width = 24

    # Save to disk
    wb.save(DATASET_EXCEL_PATH)
    print(f"Excel workbook created successfully at {DATASET_EXCEL_PATH}")

def seed_database(data):
    """Create dataset_records table and populate with all 790 conversations."""
    print("Creating database table 'dataset_records' if not exists...")
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        # Check existing count
        existing_count = db.scalar(select(func.count(DatasetRecord.id)))
        print(f"Existing rows in dataset_records: {existing_count}")

        # Upsert / insert all records
        inserted = 0
        updated = 0
        for item in data:
            cid = item["conversation_id"]
            rec = db.get(DatasetRecord, cid)
            if not rec:
                rec = DatasetRecord(
                    id=cid,
                    origin=item.get("origin", "synthetic"),
                    source_dataset=item.get("source_dataset", "Unknown"),
                    language=item.get("language", "English"),
                    script=item.get("script", "mixed"),
                    pattern_label=item.get("pattern_label", "neutral"),
                    risk_level=item.get("risk_level", "Low"),
                    target_text=item.get("target_text", ""),
                    window_text=item.get("window_text", ""),
                    rationale=item.get("rationale"),
                    turns=item.get("turns", [])
                )
                db.add(rec)
                inserted += 1
            else:
                rec.origin = item.get("origin", "synthetic")
                rec.source_dataset = item.get("source_dataset", "Unknown")
                rec.language = item.get("language", "English")
                rec.script = item.get("script", "mixed")
                rec.pattern_label = item.get("pattern_label", "neutral")
                rec.risk_level = item.get("risk_level", "Low")
                rec.target_text = item.get("target_text", "")
                rec.window_text = item.get("window_text", "")
                rec.rationale = item.get("rationale")
                rec.turns = item.get("turns", [])
                updated += 1

        db.commit()
        total_now = db.scalar(select(func.count(DatasetRecord.id)))
        print(f"Database sync complete: {inserted} inserted, {updated} updated. Total records in database: {total_now}")

def benchmark_query_speed():
    """Compare query speed between SQLite database with indexes vs reading JSON from disk."""
    print("\n" + "=" * 65)
    print("QUERY SPEED BENCHMARK: SQLITE DATABASE VS. RAW JSON FILE")
    print("=" * 65)

    iterations = 50
    test_lang = 'Hinglish'
    test_pattern = 'bullying_harassment'

    # 1. Benchmark Raw JSON disk read and filter
    start_json = time.perf_counter()
    for _ in range(iterations):
        with open(DATASET_JSON_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        filtered = [d for d in raw_data if d['language'] == test_lang and d['pattern_label'] == test_pattern]
    duration_json_ms = ((time.perf_counter() - start_json) / iterations) * 1000

    # 2. Benchmark SQLite indexed query
    start_sql = time.perf_counter()
    with SessionLocal() as db:
        for _ in range(iterations):
            stmt = select(DatasetRecord).where(
                DatasetRecord.language == test_lang,
                DatasetRecord.pattern_label == test_pattern
            )
            results = db.scalars(stmt).all()
    duration_sql_ms = ((time.perf_counter() - start_sql) / iterations) * 1000

    speedup = duration_json_ms / duration_sql_ms if duration_sql_ms > 0 else 0

    print(f"Target Query: Filter {test_lang} + {test_pattern} across 790 conversations")
    print(f"1. Raw JSON Disk Parse + Filter:  {duration_json_ms:.2f} ms per query")
    print(f"2. SQLite Indexed Database Query: {duration_sql_ms:.2f} ms per query")
    print(f"--> SPEEDUP RATIO: Database is {speedup:.1f}x FASTER than JSON disk reading!")
    print("=" * 65)

    return {
        'json_ms': round(duration_json_ms, 2),
        'sql_ms': round(duration_sql_ms, 2),
        'speedup': round(speedup, 1)
    }

def main():
    print(f"Loading dataset from {DATASET_JSON_PATH}...")
    with open(DATASET_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} conversations.")

    # 1. Excel export
    create_styled_excel(data)

    # 2. Database seeding
    seed_database(data)

    # 3. Query benchmark
    benchmark_query_speed()

if __name__ == '__main__':
    main()
