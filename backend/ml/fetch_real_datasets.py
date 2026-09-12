"""Fetch, clean, and normalize real Indian-language research datasets:
1. HASOC 2020 (Hindi hate/offensive speech)
2. BullyExplain (Hinglish code-mixed cyberbullying with rationales)
3. DravidianLangTech (Malayalam offensive language)
4. COMI-LINGUA (Hinglish clean non-toxic conversational neutral text)
"""
import re
import io
import csv
import urllib.request
import openpyxl
import pyarrow.parquet as pq

def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    # Strip URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Strip User mentions (@username)
    text = re.sub(r'@\w+', '', text)
    # Remove leading hash symbol from hashtags but keep the word
    text = re.sub(r'#(\w+)', r'\1', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_script(text: str, language: str) -> str:
    # Check for Devanagari range: \u0900-\u097F
    has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
    # Check for Malayalam range: \u0D00-\u0D7F
    has_malayalam = bool(re.search(r'[\u0D00-\u0D7F]', text))
    # Check for Latin characters
    has_latin = bool(re.search(r'[a-zA-Z]', text))

    if has_devanagari and has_latin:
        return 'mixed'
    if has_malayalam and has_latin:
        return 'mixed'
    if has_devanagari or has_malayalam:
        return 'native'
    if language in ('Hinglish', 'Manglish'):
        return 'mixed'
    return 'roman'

def fetch_hasoc_hindi(limit_per_class=45):
    """Fetch real Hindi tweets from HASOC 2020 (FIRE shared task)."""
    print("Fetching HASOC 2020 Hindi data...", flush=True)
    url = 'https://raw.githubusercontent.com/suman101112/hasoc-fire-2020/master/2020/hindi_test_1509.csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    
    samples = []
    hof_count = 0
    not_count = 0
    seen = set()

    for row in reader:
        if len(row) < 3:
            continue
        raw_text = row[1]
        task1 = row[2].strip() # HOF or NOT
        cleaned = clean_text(raw_text)
        if len(cleaned) < 15 or cleaned in seen:
            continue
        seen.add(cleaned)

        if task1 == 'HOF' and hof_count < limit_per_class:
            hof_count += 1
            samples.append({
                'source_dataset': 'HASOC-2020-Hindi',
                'language': 'Hindi',
                'script': detect_script(cleaned, 'Hindi'),
                'raw_text': cleaned,
                'pattern_label': 'bullying_harassment',
                'risk_level': 'Medium',
                'rationale': 'Hostile or offensive public comment identified in HASOC FIRE dataset.'
            })
        elif task1 == 'NOT' and not_count < limit_per_class:
            not_count += 1
            samples.append({
                'source_dataset': 'HASOC-2020-Hindi',
                'language': 'Hindi',
                'script': detect_script(cleaned, 'Hindi'),
                'raw_text': cleaned,
                'pattern_label': 'neutral',
                'risk_level': 'Low',
                'rationale': None
            })
        if hof_count >= limit_per_class and not_count >= limit_per_class:
            break

    print(f"  HASOC Hindi fetched: {len(samples)} (HOF: {hof_count}, NOT: {not_count})")
    return samples

def fetch_bullyexplain(limit_bully=50, limit_non_bully=35):
    """Fetch Hinglish cyberbullying comments with rationales from BullyExplain."""
    print("Fetching BullyExplain Hinglish data with rationales...", flush=True)
    url = 'https://github.com/Jhaprince/BullyExplain/raw/main/Dataset/BullyExplain.xlsx'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    wb = openpyxl.load_workbook(io.BytesIO(urllib.request.urlopen(req).read()))
    sheet = wb.active
    
    samples = []
    bully_count = 0
    non_bully_count = 0
    seen = set()

    # Headers: ['tweet', 'Bully_Label', 'Sentiment', 'Emotion_label', 'Sarcasm', 'Target', 'Explaine']
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        raw_text = str(row[0])
        label = str(row[1]).strip() if row[1] else ''
        rationale = str(row[6]).strip() if len(row) > 6 and row[6] else ''
        cleaned = clean_text(raw_text)
        if len(cleaned) < 15 or cleaned in seen:
            continue
        seen.add(cleaned)

        if label == 'Bully' and bully_count < limit_bully:
            bully_count += 1
            samples.append({
                'source_dataset': 'BullyExplain-Hinglish',
                'language': 'Hinglish',
                'script': 'mixed',
                'raw_text': cleaned,
                'pattern_label': 'bullying_harassment',
                'risk_level': 'Medium',
                'rationale': rationale or 'Targeted insult/humiliation identified in BullyExplain.'
            })
        elif label == 'Non_bully' and non_bully_count < limit_non_bully:
            non_bully_count += 1
            samples.append({
                'source_dataset': 'BullyExplain-Hinglish',
                'language': 'Hinglish',
                'script': 'mixed',
                'raw_text': cleaned,
                'pattern_label': 'neutral',
                'risk_level': 'Low',
                'rationale': None
            })
        if bully_count >= limit_bully and non_bully_count >= limit_non_bully:
            break

    print(f"  BullyExplain fetched: {len(samples)} (Bully: {bully_count}, Non_bully: {non_bully_count})")
    return samples

def fetch_dravidian_malayalam(limit_per_class=45):
    """Fetch Malayalam offensive/neutral comments from DravidianLangTech.
    Label mapping: 0 -> Not_offensive, 1..4 -> Offensive, 5 -> not-malayalam
    """
    print("Fetching DravidianLangTech Malayalam data...", flush=True)
    url = 'https://huggingface.co/datasets/community-datasets/offenseval_dravidian/resolve/main/malayalam/train-00000-of-00001.parquet'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    table = pq.read_table(io.BytesIO(urllib.request.urlopen(req).read()))
    
    samples = []
    off_count = 0
    not_count = 0
    seen = set()

    texts = table['text'].to_pylist()
    labels = table['label'].to_pylist()

    for raw_text, label_idx in zip(texts, labels):
        cleaned = clean_text(raw_text)
        if len(cleaned) < 15 or cleaned in seen:
            continue
        seen.add(cleaned)

        is_offensive = label_idx in (1, 2, 3, 4)
        is_neutral = (label_idx == 0)

        if is_offensive and off_count < limit_per_class:
            off_count += 1
            script = detect_script(cleaned, 'Malayalam')
            lang = 'Malayalam' if script == 'native' else 'Manglish'
            samples.append({
                'source_dataset': 'DravidianLangTech-Malayalam',
                'language': lang,
                'script': script,
                'raw_text': cleaned,
                'pattern_label': 'bullying_harassment',
                'risk_level': 'Medium',
                'rationale': f'Offensive social comment identified in DravidianLangTech corpus.'
            })
        elif is_neutral and not_count < limit_per_class:
            not_count += 1
            script = detect_script(cleaned, 'Malayalam')
            lang = 'Malayalam' if script == 'native' else 'Manglish'
            samples.append({
                'source_dataset': 'DravidianLangTech-Malayalam',
                'language': lang,
                'script': script,
                'raw_text': cleaned,
                'pattern_label': 'neutral',
                'risk_level': 'Low',
                'rationale': None
            })
        if off_count >= limit_per_class and not_count >= limit_per_class:
            break

    print(f"  Dravidian Malayalam fetched: {len(samples)} (Offensive: {off_count}, Neutral: {not_count})")
    return samples

def fetch_comi_lingua_neutral(limit=75):
    """Fetch clean, filtered non-toxic Hinglish neutral text from COMI-LINGUA."""
    print("Fetching COMI-LINGUA clean neutral Hinglish data...", flush=True)
    url = 'https://raw.githubusercontent.com/lingo-iitgn/COMI-LINGUA/main/MT_train.csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    
    samples = []
    seen = set()

    for row in reader:
        if len(row) < 2:
            continue
        raw_text = row[1] if len(row) > 1 else row[0]
        cleaned = clean_text(raw_text)
        if len(cleaned) < 20 or len(cleaned) > 200 or cleaned in seen:
            continue
        seen.add(cleaned)

        samples.append({
            'source_dataset': 'COMI-LINGUA-Hinglish',
            'language': 'Hinglish',
            'script': 'mixed',
            'raw_text': cleaned,
            'pattern_label': 'neutral',
            'risk_level': 'Low',
            'rationale': None
        })
        if len(samples) >= limit:
            break

    print(f"  COMI-LINGUA neutral fetched: {len(samples)}")
    return samples

def fetch_all_real_data():
    """Fetch, clean, and combine all 4 real dataset corpora."""
    all_real = []
    all_real.extend(fetch_hasoc_hindi(limit_per_class=45))
    all_real.extend(fetch_bullyexplain(limit_bully=50, limit_non_bully=35))
    all_real.extend(fetch_dravidian_malayalam(limit_per_class=45))
    all_real.extend(fetch_comi_lingua_neutral(limit=75))
    print(f"Total real-data entries assembled: {len(all_real)}")
    return all_real

if __name__ == '__main__':
    real_data = fetch_all_real_data()
    print("Real data breakdown:")
    sources = {}
    labels = {}
    for r in real_data:
        sources[r['source_dataset']] = sources.get(r['source_dataset'], 0) + 1
        labels[r['pattern_label']] = labels.get(r['pattern_label'], 0) + 1
    print("Sources:", sources)
    print("Labels:", labels)
