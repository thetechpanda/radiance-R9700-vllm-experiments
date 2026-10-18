#!/usr/bin/env python3
"""Summarise Pi session JSONL usage and timing without emitting message text."""
import csv
import glob
import json
import os
import sys
from datetime import datetime


def timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


def rows_for(agent_id, path):
    start = None
    number = 0
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") != "message":
                continue
            message = event.get("message") or {}
            role = message.get("role")
            event_time = timestamp(event.get("timestamp"))
            if role in ("user", "toolResult") and event_time is not None:
                start = event_time
            elif role == "assistant":
                number += 1
                usage = message.get("usage") or {}
                elapsed = round(event_time-start, 3) if event_time is not None and start is not None else ""
                yield [agent_id, number, usage.get("input", ""), usage.get("output", ""),
                       usage.get("cacheRead", ""), usage.get("cacheWrite", ""), elapsed]
                start = event_time


def main(paths):
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["agent_id", "assistant_message", "input_tokens", "output_tokens",
                     "cache_read_tokens", "cache_write_tokens", "elapsed_seconds"])
    for directory in paths:
        agent_id = os.path.basename(os.path.normpath(directory))
        sessions = sorted(glob.glob(os.path.join(directory, ".sessions", "*.jsonl")),
                          key=os.path.getmtime)
        if not sessions:
            print(f"No session JSONL found for {agent_id}", file=sys.stderr)
            continue
        for row in rows_for(agent_id, sessions[-1]):
            writer.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} WORK_DIR [WORK_DIR ...]", file=sys.stderr)
        raise SystemExit(2)
    main(sys.argv[1:])
