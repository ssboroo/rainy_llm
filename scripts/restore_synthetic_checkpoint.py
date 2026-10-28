"""Restore a trusted synthetic experiment archive outside Git, without pickle loads."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile

try:
    from .train_lora_cpu import (outside_git, checkpoint_inventory, checkpoint_step,
                                 identity_digest, CHECKPOINT_MANIFEST)
except ImportError:
    from train_lora_cpu import (outside_git, checkpoint_inventory, checkpoint_step,
                                identity_digest, CHECKPOINT_MANIFEST)

MAX_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 64


def restore(archive, sha256, destination):
    """Single-writer restore. Failed attempts remain marked incomplete; never overwrite."""
    if not re.fullmatch(r'[0-9a-f]{64}', sha256):
        raise ValueError('trusted lowercase archive SHA-256 required')
    archive = Path(archive)
    if archive.is_symlink() or not archive.is_file():
        raise ValueError('archive must be a regular local file')
    destination = outside_git(destination)
    # Use the same open descriptor for hashing and tar reads (no path reopen).
    with archive.open('rb') as stream:
        if os.fstat(stream.fileno()).st_size > MAX_BYTES:
            raise ValueError('compressed archive exceeds limit')
        h = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
        if h.hexdigest() != sha256:
            raise ValueError('archive SHA-256 mismatch')
        stream.seek(0)
        with tarfile.open(fileobj=stream, mode='r:gz') as tar:
            members, names, roots, total = [], set(), set(), 0
            for member in tar:
                name = member.name.rstrip('/')
                parts = PurePosixPath(name).parts
                if (not parts or name.startswith('/') or '\\' in name or ':' in name
                        or any(p in ('', '.', '..') for p in name.split('/'))
                        or name in names or len(members) >= MAX_MEMBERS
                        or not (member.isfile() or member.isdir()) or member.issparse()):
                    raise ValueError('unsafe or duplicate archive member')
                if member.size < 0:
                    raise ValueError('invalid member size')
                total += member.size
                if total > MAX_BYTES:
                    raise ValueError('expanded archive exceeds limit')
                names.add(name); roots.add(parts[0]); members.append(member)
            if len(roots) != 1:
                raise ValueError('archive must have exactly one run root')
            # Exclusive reservation prevents races and overwriting existing evidence.
            destination.mkdir(mode=0o700)
            marker = destination / 'RESTORE_INCOMPLETE'
            marker.write_text('Do not load this directory until restore succeeds.\n')
            run = destination / '.staging'
            run.mkdir(mode=0o700)
            for member in members:
                relative = PurePosixPath(member.name).parts[1:]
                if not relative:
                    if not member.isdir():
                        raise ValueError('root must be a directory')
                    continue
                target = run.joinpath(*relative)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with tar.extractfile(member) as source, target.open('xb') as output:
                    os.chmod(target, 0o600)
                    for chunk in iter(lambda: source.read(1024 * 1024), b''):
                        output.write(chunk)
                    output.flush(); os.fsync(output.fileno())
    identity = json.loads((run / 'identity.json').read_text())
    checkpoints = sorted(run.glob('checkpoint-*'))
    if not checkpoints:
        raise ValueError('no checkpoint in archive')
    steps = []
    for checkpoint in checkpoints:
        step = checkpoint_step(checkpoint, identity)
        expected = dict(schema=1, global_step=step,
                        run_identity_sha256=identity_digest(identity),
                        files=checkpoint_inventory(checkpoint))
        if json.loads((checkpoint / CHECKPOINT_MANIFEST).read_text()) != expected:
            raise ValueError('checkpoint integrity mismatch')
        steps.append(step)
    report = dict(schema=1, archive_sha256=sha256, restored_files=sum(m.isfile() for m in members),
                  restored_bytes=total, checkpoint_steps=steps,
                  run_identity_sha256=identity_digest(identity),
                  pickle_deserialized=False, inference_executed=False)
    with (destination / 'restore.json').open('x') as output:
        json.dump(report, output, indent=2); output.write('\n')
        output.flush(); os.fsync(output.fileno())
    run.rename(destination / 'run')
    marker.unlink()
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--destination', required=True)
    args = p.parse_args()
    try:
        print(json.dumps(restore(args.archive, args.sha256, args.destination)))
    except (ValueError, OSError, tarfile.TarError, KeyError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
