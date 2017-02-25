import sqlite3
from datetime import datetime

class ScheduleManager():
    def __init__(self, db_file_name):
        self.db_file_name = db_file_name
        self.conn = sqlite3.connect(db_file_name)
        self.cursor = self.conn.cursor()

    def create_schedule(self, name, resource_type, resource_group, action, run_probability = .5, scale_set = ""):
        command = "INSERT INTO SCHEDULES VALUES(?, ?, ?, ?, ?, ?)"
        self.cursor.execute(command, (name, resource_type, resource_group, run_probability, scale_set, action))
        self.conn.commit()

    def get_schedule(self, schedule_name):
        command = "SELECT * FROM SCHEDULES WHERE name=?"
        self.cursor.execute(command, (schedule_name,))
        return self.cursor.fetchone()

    def get_all_schedules(self):
        command = "SELECT * FROM SCHEDULES"
        self.cursor.execute(command,)
        return self.cursor.fetchall()


    