import sqlite3
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

class ProjectPersistence:
    """
    Gerencia a persistência local com arquitetura preparada para nuvem (Cloud-Ready).
    Usa UUIDs para chaves primárias para evitar colisões em futuras migrações/sincronizações.
    """
    def __init__(self, db_path: str = "mef_engine/data/structural_projects.db"):
        self.db_path = db_path
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Tabela de Projetos (Cloud-Compatible Schema)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, 
                    name TEXT NOT NULL,
                    client TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT (datetime('now', 'utc')),
                    updated_at TEXT DEFAULT (datetime('now', 'utc')),
                    sync_status TEXT DEFAULT 'local_only'
                )
            """)
            # Tabela de Cálculos (Snapshots)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    module TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    hash TEXT,
                    timestamp TEXT DEFAULT (datetime('now', 'utc')),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            # Tabela de Revisões (Notas técnicas)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revisions (
                    id TEXT PRIMARY KEY,
                    calculation_id TEXT,
                    author TEXT,
                    note TEXT,
                    timestamp TEXT DEFAULT (datetime('now', 'utc')),
                    FOREIGN KEY (calculation_id) REFERENCES calculations (id)
                )
            """)
            conn.commit()

    def create_project(self, name: str, client: str = "", description: str = "") -> str:
        project_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (id, name, client, description) VALUES (?, ?, ?, ?)",
                (project_id, name, client, description)
            )
            conn.commit()
            return project_id

    def list_projects(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def save_calculation(self, project_id: str, module: str, payload: dict, results: dict, hash_val: str) -> str:
        calc_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO calculations (id, project_id, module, payload_json, results_json, hash) VALUES (?, ?, ?, ?, ?, ?)",
                (calc_id, project_id, module, json.dumps(payload), json.dumps(results), hash_val)
            )
            # Atualiza o timestamp do projeto
            cursor.execute("UPDATE projects SET updated_at = datetime('now', 'utc') WHERE id = ?", (project_id,))
            conn.commit()
            return calc_id

    def get_project_history(self, project_id: str) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calculations WHERE project_id = ? ORDER BY timestamp DESC", (project_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_revision_note(self, calculation_id: str, author: str, note: str):
        rev_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO revisions (id, calculation_id, author, note) VALUES (?, ?, ?, ?)",
                (rev_id, calculation_id, author, note)
            )
            conn.commit()

# Singleton instance
persistence = ProjectPersistence()
