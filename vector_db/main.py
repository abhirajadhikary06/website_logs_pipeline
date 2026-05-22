from __future__ import annotations

import argparse

from vector_db.indexer import run_indexing


def main() -> None:
    parser = argparse.ArgumentParser(description="Index dbt gold models into Qdrant.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Delete existing points for each source table before upserting.",
    )
    args = parser.parse_args()

    stats = run_indexing(delete_before_upsert=args.refresh)
    print(
        "Indexing complete.",
        f"table_docs={stats['table_docs']}",
        f"row_docs={stats['row_docs']}",
    )


if __name__ == "__main__":
    main()
