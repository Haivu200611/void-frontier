# =========================
# NARRATIVE SYSTEM
# =========================

from data_loader import load_logs


class Narrative:
    def __init__(self):
        self.logs_data = load_logs()
        self.unlocked_logs = set()
        self.terminals = set()

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
    # TERMINALS (ENDING)
    # -------------------------
    def unlock_terminal(self, key):
        self.terminals.add(key)

    # -------------------------
    # PROGRESS
    # -------------------------
    def progress(self):
        return len(self.unlocked_logs)

    def get_ending(self):
        if len(self.unlocked_logs) < 10:
            return "incomplete"

        if "destroy" in self.terminals:
            return "good"

        if "escape" in self.terminals:
            return "neutral"

        return "bad"