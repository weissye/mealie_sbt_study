"""Bundle three independently audited semantic families, including first-failure evidence."""
import argparse
import json
from pathlib import Path
import zipfile
if __package__:
    from .relationship_sample_campaign import summarize_reviews
else:
    from relationship_sample_campaign import summarize_reviews


def collect(root, expected):
    families = {}
    for name in ['merge', 'quantity', 'combined']:
        folder = root/name
        reviews = sorted(folder.glob('live-*.zip'))
        families[name] = summarize_reviews(reviews, expected)
        for run in families[name]['runs']:
            if run['status'] != 'NATIVE_RELATIONSHIP_CALLBACKS_PASS':
                continue
            with zipfile.ZipFile(folder/run['review']) as archive:
                plan = json.loads(archive.read('relationship_scenario_plan.json'))
            if plan.get('semantic_program', {}).get('family') != name:
                families[name]['status'] = 'CONSISTENCY_CAMPAIGN_NOT_ACCEPTED'
                run.update(status='NOT_ACCEPTED', error='Semantic family differs from expected campaign.')
        families[name]['accepted_runs'] = sum(r['status']=='NATIVE_RELATIONSHIP_CALLBACKS_PASS' for r in families[name]['runs'])
    passed = all(f['status'] == 'CONSISTENCY_CAMPAIGN_PASS' for f in families.values())
    return {'status': 'SEMANTIC_CAMPAIGN_PASS' if passed else 'SEMANTIC_CAMPAIGN_NOT_ACCEPTED',
            'expected_runs_per_family': expected, 'families': families,
            'reset_replay_accepted': False,
            'interpretation': 'Selected explicit quantity/remapping invariants only; failures require triage.'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--expected-runs', type=int, default=3)
    args = p.parse_args()
    root = Path(args.root)
    report = collect(root, args.expected_runs)
    (root/'semantic-campaign.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    with zipfile.ZipFile(root/'campaign.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(root/'semantic-campaign.json', 'semantic-campaign.json')
        for family in ['merge', 'quantity', 'combined']:
            for file in sorted((root/family).glob('*.zip')):
                archive.write(file, family+'/'+file.name)
    print(report['status'])
    print('Review ZIP: '+str(root/'campaign.zip'))
    return 0 if report['status'] == 'SEMANTIC_CAMPAIGN_PASS' else 1
if __name__ == '__main__':
    raise SystemExit(main())
