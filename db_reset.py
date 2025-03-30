from app import app, db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def initialize_database(table_name, cs_col_name, title):
    
            db.session.execute(text(f"""
                CREATE VIRTUAL TABLE fts_{table_name} USING fts5(
                    {title},
                    tokenize = 'porter unicode61',
                    content={table_name},
                    content_rowid='id'
                )
            """))
                
            db.session.execute(text(f"""
                INSERT INTO fts_{table_name} (rowid{cs_col_name[cs_col_name.index(','):]})
                SELECT {cs_col_name} FROM {table_name}
            """))
            
            trigger_sql = [
                f"""
                CREATE TRIGGER {table_name}_ai AFTER INSERT ON {table_name}
                BEGIN
                    INSERT INTO fts_{table_name} (rowid{cs_col_name[cs_col_name.index(','):]})
                    VALUES ({",".join(["new."+ word for word in cs_col_name.split(',')])});
                END;
                """,
                f"""
                CREATE TRIGGER {table_name}_ad AFTER DELETE ON {table_name}
                BEGIN
                    INSERT INTO fts_{table_name} (fts_{table_name},rowid{cs_col_name[cs_col_name.index(','):]})
                    VALUES ('delete', {",".join(["old."+ word for word in cs_col_name.split(',')])});
                END;
                """,
                f"""
                CREATE TRIGGER {table_name}_au AFTER UPDATE ON {table_name}
                BEGIN
                    INSERT INTO fts_{table_name} (fts_{table_name},rowid{cs_col_name[cs_col_name.index(','):]})
                    VALUES ('delete', {",".join(["old."+ word for word in cs_col_name.split(',')])});
                    INSERT INTO fts_{table_name} (rowid{cs_col_name[cs_col_name.index(','):]})
                    VALUES ({",".join(["new."+ word for word in cs_col_name.split(',')])});
                END;
                """
            ]

            for sql in trigger_sql:
                db.session.execute(text(sql))
            
            db.session.commit()

with app.app_context():
    db.drop_all()
    db.create_all()
    initialize_database('user', 'id, username', 'username')
    initialize_database('subject', 'id, name', 'name')
    initialize_database('chapter', 'id, name', 'name')
    initialize_database('quiz', 'id, remarks', 'remarks')
    initialize_database('question', 'id, q_statement', 'q_statement')
    initialize_database('score', 'id, total_score', 'total_score')
    print("Datadase reset done!")