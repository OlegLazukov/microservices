from enum import Enum as SQLAlchemyEnum

class TaskStatus(SQLAlchemyEnum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
