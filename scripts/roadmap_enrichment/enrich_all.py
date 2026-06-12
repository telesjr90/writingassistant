#!/usr/bin/env python3
"""Disabled all-task enrichment entry point."""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "enrich_all.py is intentionally disabled until enrich_task.py has been proven on one task. "
        "Use enrich_task.py with an explicit task in scaffold mode."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

