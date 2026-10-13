"""Recheck the public documentation used by the HP pump review."""
import hashlib
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCES = [
    ('IDAES Pressure Changer', 'https://idaes-pse.readthedocs.io/en/stable/reference_guides/model_libraries/generic/unit_models/pressure_changer.html', ['Isentropic Assumption', 'Pump (Incompressible Fluid) Assumption', 'efficiency_isentropic']),
    ('KSB Pump efficiency', 'https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/pump-efficiency-1116510', ['power input', 'terminals of the motor']),
    ('KSB Power input', 'https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/power-input-1117260', ['pump shaft', 'Zero-flow pump input power']),
    ('KSB Efficiency class', 'https://www.ksb.com/en-global/centrifugal-pump-lexicon/article/efficiency-class-1116446', ['shaft output power', 'electrical input power']),
]
def main():
    results = []
    for title, url, terms in SOURCES:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        text = BeautifulSoup(response.text, 'html.parser').get_text(' ', strip=True)
        checks = {term: term in text for term in terms}
        assert all(checks.values()), (title, checks)
        results.append({'title': title, 'url': response.url, 'status': response.status_code,
                        'checked_date': '2026-10-13', 'html_sha256': hashlib.sha256(response.content).hexdigest(),
                        'section_or_term_presence': checks})
    out = Path(__file__).with_name('hp_pump_source_checks.json')
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'sources_verified': len(results)}))
if __name__ == '__main__':
    main()
