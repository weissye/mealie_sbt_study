import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generator_v56.render.context_observation import generate

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base-url', required=True)
    args = parser.parse_args()
    generate(args.contract, args.output, args.base_url)
    print('CONTEXT_OBSERVATION_GENERATED_NOT_EXECUTED:', args.output)
