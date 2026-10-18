#!/usr/bin/env python3
"""Derive a verified Q/K/V-only sidecar for Radiance compressed-tensors KV.

Run inside the same Radiance image as calibration. Never edits the source.
"""
import argparse
import copy
import datetime
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--model', required=True)
    args = parser.parse_args()
    from radiance_kv_calibration import validate_scale_sidecar
    from safetensors.numpy import load_file, save

    source, output = args.source, args.output
    if source.resolve() == output.resolve():
        parser.error('Source and output must be different files')
    manifest = output.with_suffix('.manifest.json')
    if output.exists() or manifest.exists():
        parser.error('Output and manifest must both be new files')
    validate_scale_sidecar(source, source_model=args.model)
    original = json.loads(source.with_suffix('.manifest.json').read_text())
    tensors = load_file(str(source))
    selected = {name: value for name, value in tensors.items()
                if name.endswith(('.q_scale', '.k_scale', '.v_scale'))}
    if not selected:
        parser.error('Source has no Q/K/V scales')
    layers = {name.rsplit('.', 1)[0] for name in selected}
    for layer in layers:
        if any(layer+'.'+kind not in selected for kind in ('q_scale', 'k_scale', 'v_scale')):
            parser.error('Incomplete Q/K/V scale triplet: '+layer)
    blob = save(selected, metadata={'format': 'radiance-fp8-kv-scales-v1'})
    derived = copy.deepcopy(original)
    derived['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    derived['artifact'] = {'filename': output.name, 'sha256': hashlib.sha256(blob).hexdigest(),
                           'tensor_count': len(selected)}
    derived['derivation'] = {'operation': 'Retain Q/K/V scales; remove probability scales for compressed-tensors KV',
                             'source_artifact_sha256': original['artifact']['sha256']}
    # Keep the original model identity, observations and software provenance.
    with output.open('xb') as stream:
        stream.write(blob)
    with manifest.open('x') as stream:
        json.dump(derived, stream, indent=2, sort_keys=True)
        stream.write('\n')
    validate_scale_sidecar(output, source_model=args.model)
    print(f'Verified {len(selected)} scales across {len(layers)} attention layers: {output}')


if __name__ == '__main__':
    main()
