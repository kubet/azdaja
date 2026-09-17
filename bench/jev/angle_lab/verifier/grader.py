"""Grade actual external verifier labels, never manufacture model outputs."""
import json
from pathlib import Path
from .prepare import make_pack
from bench.jev.angle_lab.native import canonical

HERE=Path(__file__).parent


def grade(answers):
    pack=json.loads((HERE/'pack.json').read_text())
    if canonical(pack)!=canonical(make_pack()):
        raise ValueError('source pack is not the frozen Git-derived contract')
    gold=json.loads((HERE/'gold.json').read_text())['labels']
    if not isinstance(answers,dict) or set(answers)!=set(gold):
        raise ValueError('exact ID coverage required')
    if any(label not in ('supported','contradicted','insufficient') for label in answers.values()):
        raise ValueError('invalid label')
    valid=[key for key in gold if gold[key]=='supported']
    flawed=[key for key in gold if gold[key]!='supported']
    return {'correct':sum(answers[key]==gold[key] for key in gold),'total':len(gold),
            'valid_claims':len(valid),'flawed_claims':len(flawed),
            'false_alarms':[key for key in valid if answers[key]!='supported'],
            'flawed_retained':[key for key in flawed if answers[key]=='supported'],
            'screen_pass':answers==gold,
            'rows':[{'id':key,'actual':answers[key],'expected':gold[key]} for key in gold],
            'prose_repair_measured':False}
