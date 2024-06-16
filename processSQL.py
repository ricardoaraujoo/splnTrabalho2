import sqlite3

def import_sql_dump_chunked(sql_file_path, db_path, commit_interval=1000):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create the table if it does not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS dreapp_document (
            id INTEGER PRIMARY KEY,
            document_id INTEGER,
            document_type TEXT,
            document_number TEXT,
            entity TEXT,
            journal TEXT,
            reference TEXT,
            published BOOLEAN,
            canceled BOOLEAN,
            publication_date TEXT,
            content TEXT,
            url TEXT,
            pdf_url TEXT,
            deleted BOOLEAN,
            created_at TEXT,
            updated BOOLEAN,
            metadata_version TEXT,
            document_version INTEGER,
            external_id TEXT
        );
    ''')
    conn.commit()

    # Create the table if it does not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS dreapp_documenttext (
            id INTEGER PRIMARY KEY,
            document_id INTEGER,
            publication_date TEXT,
            url TEXT,
            content TEXT
        );
    ''')
    conn.commit()



    # Initialize variables
    commands_executed = 0

    # Open and process the SQL dump file
    with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
        command = ''  # Use a string to collect parts of the command
        for line in sql_file:
            if not line.startswith('--') and not line.startswith('SET') and 'pg_catalog' not in line:
                command += line  # Append the line to the command string
                if line.strip().endswith(';'):  # Check if the command ends
                    print(f"Command to execute: {command}")
                    try:
                        cur.execute(command)
                        print(f"Command executed: {command}")
                        commands_executed += 1
                    except sqlite3.Error as e:
                        print(f"Error executing command: {e}")
                    command = ''  # Reset the command string

                    if commands_executed % commit_interval == 0:
                        conn.commit()
                        print(f"Committed {commands_executed} commands")

    # Final commit for any remaining commands
    conn.commit()
    conn.close()
    print(f"Finished importing. Total commands executed: {commands_executed}")

# Example usage
sql_file_path = 'dataset/converted_database.sql'
db_path = 'dataset/database111_DRE.sqlite'
import_sql_dump_chunked(sql_file_path, db_path)