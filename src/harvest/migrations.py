import sqlite3
import shutil
import argparse

def run(as_of: str = None, limit: int = None):
    db_path = 'data/state/cursor.db'
    db = sqlite3.connect(db_path)
    
    cur = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='capture_unit'")
    row = cur.fetchone()
    if row and "branch_runs" in row[0]:
        print("Migration already applied: branch_runs is in capture_unit kind CHECK constraint.")
        return
        
    shutil.copy2(db_path, db_path + '.bak')
    db.isolation_level = None # autocommit mode

    with db:
        db.execute('BEGIN')
        db.execute('CREATE TABLE capture_unit_new ('
            'repo          TEXT NOT NULL,'
            'kind          TEXT NOT NULL CHECK (kind IN ('
                "'pulls', 'pull_files', 'pull_commits', 'runs',"
                "'jobs', 'checkruns', 'annotations', 'artifacts', 'logs',"
                "'branch_runs'"
            ')),'
            'unit_key      TEXT NOT NULL,'
            'status        TEXT NOT NULL CHECK (status IN ('
                "'in_flight', 'complete', 'skipped', 'expired', 'failed'"
            ')),'
            'parent_run_id INTEGER,'
            'started_at    TEXT NOT NULL,'
            'completed_at  TEXT,'
            'reason        TEXT,'
            'PRIMARY KEY (repo, kind, unit_key)'
        ')')
        db.execute('INSERT INTO capture_unit_new SELECT * FROM capture_unit')
        db.execute('DROP TABLE capture_unit')
        db.execute('ALTER TABLE capture_unit_new RENAME TO capture_unit')
        db.execute('COMMIT')

    print("Migration successful.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", type=str, help="As of date")
    parser.add_argument("--limit", type=int, help="Limit (ignored)")
    args = parser.parse_args()
    run(as_of=args.as_of, limit=args.limit)
