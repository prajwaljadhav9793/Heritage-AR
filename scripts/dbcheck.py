import sqlite3

con = sqlite3.connect("data/vector_db/chroma.sqlite3")
tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
print("tables:", tables)
for t in ("embeddings", "segments", "collections"):
    if t in tables:
        cols = [r[1] for r in con.execute(f"pragma table_info({t})")]
        print(t, "cols:", cols)
con.close()
con = sqlite3.connect("data/vector_db/chroma.sqlite3")
cur = con.execute(
    "select count(*) from embeddings e join segments s on e.segment_id=s.id "
    "join collections c on s.collection=c.id "
    "where c.name='heritage_knowledge'"
)
print("total embeddings:", cur.fetchone()[0])
cur = con.execute(
    "select count(*) from embedding_metadata where key='source' "
    "and string_value='Khajuraho Group of Monuments.docx'"
)
print("khajuraho chunks:", cur.fetchone()[0])

tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
print("tables:", tables)
for t in ("embeddings", "segments", "collections"):
    if t in tables:
        cols = [r[1] for r in con.execute(f"pragma table_info({t})")]
        print(t, "cols:", cols)
