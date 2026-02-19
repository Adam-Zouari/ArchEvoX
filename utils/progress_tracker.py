"""
Progress Tracker for Dashboard Integration
Emits real-time progress updates to a JSON file that the dashboard reads
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
import threading

class ProgressTracker:
    """Thread-safe progress tracker for pipeline visualization"""

    def __init__(self, output_file: str = "outputs/progress.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.data = {
            "status": "idle",
            "start_time": None,
            "end_time": None,
            "total_proposals": 0,
            "proposals": [],
            "stages": {}
        }
        self._save()

    def start_pipeline(self):
        """Mark pipeline as started"""
        with self.lock:
            self.data["status"] = "running"
            self.data["start_time"] = datetime.now().isoformat()
            self.data["end_time"] = None
            self._save()

    def end_pipeline(self, success: bool = True):
        """Mark pipeline as completed"""
        with self.lock:
            self.data["status"] = "completed" if success else "error"
            self.data["end_time"] = datetime.now().isoformat()
            self._save()

    def start_stage(self, stage_id: str, stage_name: str):
        """Mark a stage as started"""
        with self.lock:
            stage_key = f"stage_{stage_id}"
            self.data[stage_key] = {
                "name": stage_name,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "progress": 0,
                "outputs_count": 0,
                "details": {},
                "error": None
            }
            self._save()

    def update_stage_progress(self, stage_id: str, progress: int, details: Dict[str, Any] = None):
        """Update stage progress (0-100)"""
        with self.lock:
            stage_key = f"stage_{stage_id}"
            if stage_key in self.data:
                self.data[stage_key]["progress"] = progress
                if details:
                    self.data[stage_key]["details"].update(details)
                self._save()

    def end_stage(self, stage_id: str, outputs_count: int = 0, success: bool = True, error: str = None):
        """Mark a stage as completed"""
        with self.lock:
            stage_key = f"stage_{stage_id}"
            if stage_key in self.data:
                self.data[stage_key]["status"] = "completed" if success else "error"
                self.data[stage_key]["end_time"] = datetime.now().isoformat()
                self.data[stage_key]["progress"] = 100 if success else 0
                self.data[stage_key]["outputs_count"] = outputs_count
                if error:
                    self.data[stage_key]["error"] = error

                # Calculate duration
                start = datetime.fromisoformat(self.data[stage_key]["start_time"])
                end = datetime.fromisoformat(self.data[stage_key]["end_time"])
                self.data[stage_key]["duration"] = (end - start).total_seconds()

                self._save()

    def skip_stage(self, stage_id: str, reason: str = "Disabled in config"):
        """Mark a stage as skipped"""
        with self.lock:
            stage_key = f"stage_{stage_id}"
            self.data[stage_key] = {
                "status": "skipped",
                "reason": reason
            }
            self._save()

    def add_proposal(self, proposal: Dict[str, Any]):
        """Add a generated proposal to the progress data"""
        with self.lock:
            # Extract key fields for display
            proposal_summary = {
                "architecture_name": proposal.get("architecture_name"),
                "paradigm_source": proposal.get("paradigm_source"),
                "core_thesis": proposal.get("core_thesis"),
                "components": proposal.get("components", []),
                "key_innovations": proposal.get("key_innovations", []),
                "scores": proposal.get("scores"),
                "timestamp": datetime.now().isoformat()
            }
            self.data["proposals"].append(proposal_summary)
            self.data["total_proposals"] = len(self.data["proposals"])
            self._save()

    def add_proposals_batch(self, proposals: List[Dict[str, Any]]):
        """Add multiple proposals at once"""
        for proposal in proposals:
            self.add_proposal(proposal)

    def update_proposal_scores(self, architecture_name: str, scores: Dict[str, float]):
        """Update scores for a specific proposal"""
        with self.lock:
            for proposal in self.data["proposals"]:
                if proposal["architecture_name"] == architecture_name:
                    proposal["scores"] = scores
            self._save()

    def set_custom_data(self, key: str, value: Any):
        """Set custom data in the progress tracker"""
        with self.lock:
            self.data[key] = value
            self._save()

    def save_debate_results(self, debate_results: List[Any]):
        """Save structured debate results for later use"""
        with self.lock:
            # Convert to dict for JSON serialization
            self.data["debate_results"] = [dr.model_dump() if hasattr(dr, 'model_dump') else dr for dr in debate_results]
            self._save()

    def save_critic_results(self, critic_results: Dict[str, Any]):
        """Save domain critic results for later use"""
        with self.lock:
            # Convert to dict for JSON serialization
            self.data["critic_results"] = {
                arch_name: cr.model_dump() if hasattr(cr, 'model_dump') else cr
                for arch_name, cr in critic_results.items()
            }
            self._save()

    def _save(self):
        """Save progress data to file (must be called within lock)"""
        try:
            with open(self.output_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save progress data: {e}")

    def get_data(self) -> Dict[str, Any]:
        """Get current progress data"""
        with self.lock:
            return self.data.copy()


# Global instance
_tracker = None

def get_tracker() -> ProgressTracker:
    """Get or create global progress tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = ProgressTracker()
    return _tracker
