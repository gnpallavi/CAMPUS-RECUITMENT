# TODO: Migrate from MySQL to SQLite

## Tasks to Complete:
- [x] Update `app.py` to change database URI to SQLite ('sqlite:///instance/placement.db')
- [x] Update `requirements.txt` to add `mysql-connector-python` for migration
- [x] Create `migrate_to_sqlite.py` script to export data from MySQL and import to SQLite
- [x] Run the migration script to copy data
- [x] Remove `mysql-connector-python` from `requirements.txt` after migration
- [x] Test the app with SQLite to ensure functionality
- [x] Delete `migrate_to_sqlite.py` if no longer needed
