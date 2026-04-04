#!/usr/bin/env python3
"""dotenv_tool - .env file manager.

Parse, validate, diff, merge, and generate .env files. Zero dependencies.
"""

import argparse
import os
import re
import sys


def parse_env(path):
    """Parse .env file into ordered list of (key, value, comment) tuples."""
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                entries.append((None, None, line))
                continue
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)', line)
            if m:
                key = m.group(1)
                val = m.group(2).strip().strip('"').strip("'")
                entries.append((key, val, None))
            else:
                entries.append((None, None, line))
    return entries


def to_dict(entries):
    return {k: v for k, v, _ in entries if k is not None}


def cmd_parse(args):
    entries = parse_env(args.file)
    d = to_dict(entries)
    if args.json:
        import json
        print(json.dumps(d, indent=2))
    elif args.key:
        if args.key in d:
            print(d[args.key])
        else:
            print(f"Key not found: {args.key}", file=sys.stderr)
            sys.exit(1)
    else:
        for k, v in sorted(d.items()):
            print(f"{k}={v}")


def cmd_set(args):
    entries = parse_env(args.file)
    d = to_dict(entries)
    found = False
    new_entries = []
    for k, v, c in entries:
        if k == args.key:
            new_entries.append((k, args.value, None))
            found = True
        else:
            new_entries.append((k, v, c))
    if not found:
        new_entries.append((args.key, args.value, None))
    with open(args.file, "w") as f:
        for k, v, c in new_entries:
            if k is not None:
                f.write(f"{k}={v}\n")
            else:
                f.write(f"{c}\n")
    print(f"{'Updated' if found else 'Added'}: {args.key}")


def cmd_unset(args):
    entries = parse_env(args.file)
    new_entries = [(k, v, c) for k, v, c in entries if k != args.key]
    if len(new_entries) == len(entries):
        print(f"Key not found: {args.key}", file=sys.stderr)
        sys.exit(1)
    with open(args.file, "w") as f:
        for k, v, c in new_entries:
            if k is not None:
                f.write(f"{k}={v}\n")
            else:
                f.write(f"{c}\n")
    print(f"Removed: {args.key}")


def cmd_diff(args):
    a = to_dict(parse_env(args.file1))
    b = to_dict(parse_env(args.file2))
    all_keys = sorted(set(list(a.keys()) + list(b.keys())))
    added = removed = changed = same = 0
    for k in all_keys:
        if k in a and k not in b:
            print(f"  - {k}={a[k]}")
            removed += 1
        elif k not in a and k in b:
            print(f"  + {k}={b[k]}")
            added += 1
        elif a[k] != b[k]:
            print(f"  ~ {k}: {a[k]!r} → {b[k]!r}")
            changed += 1
        else:
            same += 1
    print(f"\n{added} added, {removed} removed, {changed} changed, {same} same", file=sys.stderr)


def cmd_merge(args):
    base = parse_env(args.base)
    overlay = to_dict(parse_env(args.overlay))
    base_dict = to_dict(base)
    result = []
    seen = set()
    for k, v, c in base:
        if k is not None and k in overlay:
            result.append((k, overlay[k], None))
            seen.add(k)
        else:
            result.append((k, v, c))
            if k:
                seen.add(k)
    for k, v in overlay.items():
        if k not in seen:
            result.append((k, v, None))
    for k, v, c in result:
        if k is not None:
            print(f"{k}={v}")
        else:
            print(c)


def cmd_validate(args):
    entries = parse_env(args.file)
    d = to_dict(entries)
    issues = []
    for k, v in d.items():
        if not v:
            issues.append(f"  ⚠ {k}: empty value")
        if " " in k:
            issues.append(f"  ✗ {k}: spaces in key name")
    # Check for required keys
    if args.required:
        for req in args.required:
            if req not in d:
                issues.append(f"  ✗ {req}: missing (required)")
    if issues:
        print(f"Issues ({len(issues)}):")
        for i in issues:
            print(i)
        sys.exit(1)
    else:
        print(f"✓ Valid ({len(d)} variables)")


def cmd_template(args):
    entries = parse_env(args.file)
    d = to_dict(entries)
    for k in sorted(d.keys()):
        print(f"{k}=")


def main():
    p = argparse.ArgumentParser(description=".env file manager")
    sub = p.add_subparsers(dest="cmd")

    pp = sub.add_parser("parse", help="Parse and display .env")
    pp.add_argument("file")
    pp.add_argument("-k", "--key", help="Get specific key")
    pp.add_argument("--json", action="store_true")

    sp = sub.add_parser("set", help="Set a variable")
    sp.add_argument("file")
    sp.add_argument("key")
    sp.add_argument("value")

    up = sub.add_parser("unset", help="Remove a variable")
    up.add_argument("file")
    up.add_argument("key")

    dp = sub.add_parser("diff", help="Diff two .env files")
    dp.add_argument("file1")
    dp.add_argument("file2")

    mp = sub.add_parser("merge", help="Merge overlay onto base")
    mp.add_argument("base")
    mp.add_argument("overlay")

    vp = sub.add_parser("validate", help="Validate .env file")
    vp.add_argument("file")
    vp.add_argument("-r", "--required", nargs="+", help="Required keys")

    tp = sub.add_parser("template", help="Generate template (keys only)")
    tp.add_argument("file")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)
    {"parse": cmd_parse, "set": cmd_set, "unset": cmd_unset, "diff": cmd_diff,
     "merge": cmd_merge, "validate": cmd_validate, "template": cmd_template}[args.cmd](args)


if __name__ == "__main__":
    main()
