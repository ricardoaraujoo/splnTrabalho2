import re

def convert_line(line):
    # Remove type casts
    line = re.sub(r'::[a-zA-Z0-9_]+', '', line)
    # Replace SERIAL with AUTOINCREMENT
    line = re.sub(r'SERIAL', 'INTEGER PRIMARY KEY AUTOINCREMENT', line)
    # Replace BOOLEAN with INTEGER
    line = re.sub(r'BOOLEAN', 'INTEGER', line)
    # Remove sequences
    line = re.sub(r'CREATE SEQUENCE.*?;', '', line, flags=re.DOTALL)
    # Replace sequence usage with NULL
    line = re.sub(r'nextval\([^)]*\)', 'NULL', line)
    # Remove timestamp type casts
    line = re.sub(r'\'\d+\.\d+\'::timestamp', lambda x: x.group(0).replace("::timestamp", ""), line)
    # Remove date type casts
    line = re.sub(r'\'\d+-\d+-\d+\'::date', lambda x: x.group(0).replace("::date", ""), line)
    # Remove time type casts
    line = re.sub(r'\'\d+:\d+:\d+\'::time', lambda x: x.group(0).replace("::time", ""), line)
    # Remove interval type casts
    line = re.sub(r'\'\d+\.\d+\'::interval', lambda x: x.group(0).replace("::interval", ""), line)
    # Remove ONLY from ALTER TABLE
    line = re.sub(r'ALTER TABLE ONLY', 'ALTER TABLE', line)
    # Remove OWNER TO
    line = re.sub(r'OWNER TO.*?;', '', line)
    # Remove comments
    line = re.sub(r'COMMENT ON.*?;', '', line)
    # Remove USING btree in CREATE INDEX
    line = re.sub(r'USING btree', '', line)
    # Remove 'public.' schema prefix
    line = re.sub(r'public\.', '', line)

    # Replace boolean values
    def replace_booleans(match):
        match_str = match.group(0)
        return match_str.replace('true', '1').replace('false', '0')

    line = re.sub(r'(?<!\')\btrue\b(?!\')|(?<!\')\bfalse\b(?!\')', replace_booleans, line, flags=re.IGNORECASE)

    # Remove PostgreSQL-specific settings
    line = re.sub(r'SET [^\n]+;\n', '', line)
    line = re.sub(r'SELECT pg_catalog.set_config[^\n]+;\n', '', line)

    return line

def convert_postgresql_to_sqlite(postgresql_file, sqlite_file):
    with open(postgresql_file, 'r') as infile, open(sqlite_file, 'w') as outfile:
        for line in infile:
            converted_line = convert_line(line)
            outfile.write(converted_line)

# Specify the PostgreSQL SQL dump file and the SQLite SQL file
postgresql_file = 'dataset/2024-04-07-DRE_dump.sql'
sqlite_file = 'dataset/converted_database.sql'

# Convert PostgreSQL SQL dump to SQLite-compatible SQL
convert_postgresql_to_sqlite(postgresql_file, sqlite_file)
