import uuid
import threading
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobManager:
    """
    Gestor de Jobs Assíncronos para Análises Estruturais Pesadas.
    Permite rastrear o progresso de cálculos em edifícios de grande escala.
    """
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        with self.lock:
            self.jobs[job_id] = {
                "id": job_id,
                "type": job_type,
                "status": JobStatus.PENDING,
                "progress": 0,
                "created_at": datetime.now().isoformat(),
                "result": None,
                "error": None
            }
        return job_id

    def update_job(self, job_id: str, status: Optional[JobStatus] = None, progress: Optional[int] = None, result: Any = None, error: str = None):
        with self.lock:
            if job_id in self.jobs:
                if status: self.jobs[job_id]["status"] = status
                if progress is not None: self.jobs[job_id]["progress"] = progress
                if result is not None: self.jobs[job_id]["result"] = result
                if error: self.jobs[job_id]["error"] = error
                if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    self.jobs[job_id]["finished_at"] = datetime.now().isoformat()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            return self.jobs.get(job_id)

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self.lock:
            return list(self.jobs.values())

# Instância global para ser usada pelos routers
job_manager = JobManager()
