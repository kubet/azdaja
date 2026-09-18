"""Provider-free artifact checks. Exact evidence is not semantic correctness."""
import argparse
import json
from pathlib import Path


def verify(work, sources):
    failures = []
    result = {'output_files': {n: (work / n).is_file() for n in ('risk.py', 'risk.json', 'REPORT.md')},
              'semantic_accuracy': 'not_established', 'script_reproduction': 'not_yet_executed',
              'report_counts': 'requires_independent_check', 'report_quotes': 0,
              'records': 0, 'positive_fields': 0, 'evidence_spans': 0,
              'counts': {'assignment': 0, 'exclusivity': 0}, 'failures': failures}
    if not all(result['output_files'].values()):
        failures.append('missing_required_artifact')
    try:
        rows = json.loads((work / 'risk.json').read_text())
    except (OSError, ValueError):
        failures.append('missing_or_invalid_risk_json')
        result['structural_acceptance'] = False
        return result
    if not isinstance(rows, list):
        failures.append('risk_json_not_array')
        result['structural_acceptance'] = False
        return result
    result['records'] = len(rows)
    expected = sorted(sources)
    actual = [r.get('file') if isinstance(r, dict) else None for r in rows]
    if actual != expected:
        failures.append('file_coverage_or_order')
    report = (work / 'REPORT.md').read_text() if (work / 'REPORT.md').is_file() else ''
    quoted = set()
    for row in rows:
        if not isinstance(row, dict) or row.get('file') not in sources:
            failures.append('invalid_record_identity')
            continue
        name = row['file']
        raw = (work / 'corpus' / name).read_bytes()
        if type(row.get('size_bytes')) is not int or row['size_bytes'] != len(raw):
            failures.append(name + ':size_bytes')
        for category in ('assignment', 'exclusivity'):
            value = row.get(category)
            if not isinstance(value, dict) or value.get('answer') not in ('yes', 'no') or not isinstance(value.get('evidence'), list):
                failures.append(name + ':' + category + ':invalid_field')
                continue
            yes = value['answer'] == 'yes'
            result['counts'][category] += int(yes)
            result['positive_fields'] += int(yes)
            if yes != bool(value['evidence']):
                failures.append(name + ':' + category + ':evidence_presence')
            for evidence in value['evidence']:
                if not isinstance(evidence, dict):
                    failures.append(name + ':invalid_evidence')
                    continue
                start, end, quote = (evidence.get(k) for k in ('start', 'end', 'quote'))
                if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(raw)
                        or not isinstance(quote, str) or raw[start:end] != quote.encode('utf-8')):
                    failures.append(name + ':invalid_byte_quote')
                    continue
                result['evidence_spans'] += 1
                # This is a lower-bound exact textual witness, not a complete Markdown parser.
                if quote in report and name in report and str(start) in report and str(end) in report:
                    quoted.add((name, start, end))
    result['report_quotes'] = len(quoted)
    result['structural_acceptance'] = not failures
    result['full_task_acceptance'] = 'pending_offline_script_and_report_review'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.work, {p.name: None for p in (args.work / 'corpus').glob('*.txt')}), indent=2))
