import sqlite3
import os
import sys
import psycopg2

# Connect to sqlite database
sqlite_conn = sqlite3.connect(sys.argv[1])
sqlite_cursor = sqlite_conn.cursor()

# Create postgres database
postgres_conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
postgres_cursor = postgres_conn.cursor()

create_db = """
BEGIN;

CREATE TABLE genbanks(
    id TEXT PRIMARY KEY, 
    description TEXT,
    organism TEXT
);

CREATE TABLE codons (
    codon TEXT NOT NULL,
    codon_count INTEGER NOT NULL,
    amino_acid TEXT NOT NULL CHECK (amino_acid IN ('{}')),
    transl_table SMALLINT,
    genbank_id TEXT REFERENCES genbanks(id),
    PRIMARY KEY(codon,amino_acid,genbank_id)
);

COMMIT;
""".format("','".join('ARNDBCEQZGHILKMFPSTWYV*X'))
postgres_cursor.execute(create_db)
postgres_conn.commit()

# Add organisms from sqlite into genbanks on postgres
for row in sqlite_cursor.execute('SELECT id, description, organism FROM organisms').fetchall():
    postgres_cursor.execute('INSERT INTO genbanks(id,description,organism) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING',(row[0],row[1],row[2]))
postgres_conn.commit()

# Add codons from sqlite into codons on postgres
for i,row in enumerate(sqlite_cursor.execute('SELECT codon, codon_count, amino_acid, organism FROM codons').fetchall()):
    postgres_cursor.execute('INSERT INTO codons(codon,codon_count,amino_acid,genbank_id) VALUES(%s,%s,%s,%s)',(row[0],row[1],row[2],row[3]))
    if (i % 100000000 == 0): # Commit every 100,000,000 lines
        postgres_conn.commit()
postgres_conn.commit()

