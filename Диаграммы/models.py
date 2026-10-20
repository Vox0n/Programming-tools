# file: models.py
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, EmailStr


# --- Сущности ---

class ServicePackage(BaseModel):
    id: str
    name: str
    sessions_count: int = Field(gt=0)
    price: float = Field(gt=0)
    purchase_date: datetime


class ChatMessage(BaseModel):
    id: str
    text: str
    timestamp: datetime
    sender_role: str  # "Trainer" или "Client"


class NutritionLog(BaseModel):
    id: str
    date: datetime
    food_items: str
    total_calories: float = Field(ge=0)
    total_proteins: float = Field(ge=0)
    total_fats: float = Field(ge=0)
    total_carbs: float = Field(ge=0)


class ProgressRecord(BaseModel):
    id: str
    date: datetime
    client_weight: float = Field(gt=0)
    working_weight: float = Field(ge=0)
    exercise_name: str


class ScheduledWorkout(BaseModel):
    id: str
    date_time: datetime
    status: str = "Planned"  # Planned, InProgress, Completed, Missed


class Client(BaseModel):
    id: str
    name: str
    goal: str
    height: float
    weight: float
    age: int

    # Связи
    packages: List[ServicePackage] = []
    nutrition_logs: List[NutritionLog] = []
    progress_history: List[ProgressRecord] = []
    chat_history: List[ChatMessage] = []

    def calculate_bmr(self) -> float:
        """Пример бизнес-логики: расчет базового метаболизма (BMR)"""
        # Упрощенная формула Миффлина-Сан Жеора
        return (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5

    def add_nutrition_log(self, log: NutritionLog) -> None:
        self.nutrition_logs.append(log)
        print(f"Добавлена запись о питании для {self.name}. Калории: {log.total_calories}")


class Trainer(BaseModel):
    id: str
    name: str
    email: EmailStr

    # Связи
    clients: List[Client] = []
    schedule: List[ScheduledWorkout] = []
    chat_history: List[ChatMessage] = []

    def add_client(self, client: Client) -> None:
        self.clients.append(client)
        print(f"Тренер {self.name} зарегистрировал клиента {client.name}")

    def view_nutrition_report(self, client_id: str) -> List[NutritionLog]:
        """Тренер запрашивает отчет по питанию клиента"""
        client = next((c for c in self.clients if c.id == client_id), None)
        if client:
            return client.nutrition_logs
        return []


# --- Пример использования (Демонстрация) ---
if __name__ == "__main__":
    # Создаем тренера
    trainer = Trainer(id="t1", name="Иван Петров", email="ivan@fit.ru")

    # Создаем клиента
    client = Client(
        id="c1",
        name="Алексей Смирнов",
        goal="Набор мышечной массы",
        height=180.0,
        weight=75.5,
        age=25
    )

    # Тренер добавляет клиента
    trainer.add_client(client)

    # Назначаем пакет услуг
    package = ServicePackage(
        id="p1",
        name="Пакет 10 тренировок",
        sessions_count=10,
        price=20000,
        purchase_date=datetime.now()
    )
    client.packages.append(package)

    # Клиент заполняет дневник питания
    nutrition = NutritionLog(
        id="n1",
        date=datetime.now(),
        food_items="Куриная грудка 200г, Рис 100г",
        total_calories=450.0,
        total_proteins=40.0,
        total_fats=5.0,
        total_carbs=50.0
    )
    client.add_nutrition_log(nutrition)

    # Тренер смотрит отчет
    report = trainer.view_nutrition_report("c1")
    print(f"\nТренер видит записей о питании: {len(report)}")
    print(f"Последний прием пищи: {report[0].food_items}")

    # Расчет BMR клиента
    print(f"Базовый метаболизм клиента: {client.calculate_bmr()} ккал")
