import sqlite3

def query_by_ids(db_path, document_ids):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Prepare the placeholders for the query based on the number of document_ids
    placeholders = ','.join('?' for _ in document_ids)
    
    # Query the document_details table for multiple IDs
    cur.execute(f'SELECT * FROM dreapp_document WHERE id IN ({placeholders})', document_ids)
    details_result = cur.fetchall()
    
    # Query the dreapp_documenttext table for multiple IDs
    cur.execute(f'SELECT * FROM dreapp_documenttext WHERE document_id IN ({placeholders})', document_ids)
    text_result = cur.fetchall()
    
    conn.close()

    ids = set()

    for result in text_result:
        ids.add(result[1])
    
    for result in details_result:
        ids.add(result[0])


    resultados = []
    for id in ids:
        found = False
        for result in text_result:
            if result[1] == id:
                resultados.append(result)
                found = True
                break
        if not found:
            for result in details_result:
                if result[0] == id:
                    resultados.append(result)
                    break

    return resultados