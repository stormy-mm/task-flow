from dataclasses import dataclass

@dataclass
class TaskDTO:
    """Класс для представления задачи"""
    id: int
    title: str
    status : str
    description: str