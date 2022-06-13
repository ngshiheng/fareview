#!/bin/bash
BRANDS=("carlsberg" "tiger" "heineken" "guinness" "asahi")

PGDATABASE="${PGDATABASE-fareview}"
PGHOST="${PGHOST-localhost}"
PGPASSWORD="${PGPASSWORD-}"
PGPORT="${PGPORT-5432}"
PGUSER="${PGUSER-postgres}"

mkdir -p data/
for brand in "${BRANDS[@]}"; do
    PGPASSWORD=$PGPASSWORD psql -v brand="'${brand}'" -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -F ',' -A --pset footer -f alembic/examples/get_all_by_brand.sql >"data/${brand}.csv"
done
