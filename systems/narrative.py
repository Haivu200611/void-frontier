# =========================
# NARRATIVE SYSTEM
# =========================

from data_loader import load_logs
from settings import TOTAL_LOGS, TOTAL_TERMINALS


class Narrative:
    def __init__(self):
        self.logs_data = load_logs()
        self.unlocked_logs = set()
        self.terminals = set()
        self.final_choice = None

    # -------------------------
    # LOGS
    # -------------------------
    def unlock_log(self, log_id):
        if log_id in self.logs_data:
            self.unlocked_logs.add(log_id)

    def get_log(self, log_id):
        return self.logs_data.get(log_id)

    def get_all_logs(self):
        return [self.logs_data[i] for i in sorted(self.unlocked_logs)]

    # -------------------------
    # TERMINALS
    # -------------------------
    def unlock_terminal(self, terminal_key):
        self.terminals.add(terminal_key)

    def can_reach_true_endgame(self):
        return len(self.unlocked_logs) >= TOTAL_LOGS and len(self.terminals) >= TOTAL_TERMINALS

    # -------------------------
    # ENDING
    # -------------------------
    def set_final_choice(self, choice):
        self.final_choice = choice

    def get_ending(self):
        if self.final_choice == "destroy_xenite":
            return "good"
        if self.final_choice == "call_earth":
            return "neutral"
        if self.final_choice == "take_xenite":
            return "bad"

        if self.can_reach_true_endgame():
            return "pending_choice"
        return "incomplete"

    # -------------------------
    # PROGRESS
    # -------------------------
    def logs_progress(self):
        return len(self.unlocked_logs), TOTAL_LOGS

    def terminals_progress(self):
        return len(self.terminals), TOTAL_TERMINALS

    def progress(self):
        return len(self.unlocked_logs)
