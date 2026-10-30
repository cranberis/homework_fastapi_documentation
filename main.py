from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Path
from pydantic import BaseModel, Field

app = FastAPI()


class TaskCreate(BaseModel):
    """Модель входных данных для создания задачи."""

    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: str | None = Field(
        default=None, description="Описание задачи (опционально)"
    )
    priority: int = Field(..., ge=1, le=5, description="Приоритет от 1 до 5")


class TaskResponse(BaseModel):
    """Модель ответа с данными задачи."""

    id: int = Field(..., description="Уникальный идентификатор задачи")
    title: str = Field(..., description="Название задачи")
    description: str | None = Field(default=None, description="Описание задачи")
    priority: int = Field(..., description="Приоритет задачи")
    created_at: datetime = Field(..., description="Дата и время создания")


# Хранилище в памяти (заглушка вместо БД)
tasks_db: list[dict] = []


# Эндпоинт создания задачи
@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse,
    summary="Создание новой задачи",
    description="""
        Создаёт новую задачу в системе управления задачами.
        Входные данные проходят валидацию: title (3-100 символов), description (опционально), priority (1-5).
        Поля id и created_at генерируются автоматически на сервере.
        """,
    responses={
        201: {"description": "Задача успешно создана"},
    },
)
async def create_task(task: TaskCreate):
    """Создание новой задачи в системе управления задачами."""

    # Генерируем id (автоинкремент)
    new_id = len(tasks_db) + 1 if tasks_db else 1

    # Создаём задачу
    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "created_at": datetime.now(),
    }

    # Сохраняем в хранилище
    tasks_db.append(new_task)

    # Возвращаем созданную задачу
    return new_task


# Эндпоинт получения задачи по ID
@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Получение задачи по идентификатору",
    description="""
        Возвращает задачу по указанному идентификатору task_id. 
        При успешном поиске возвращает объект задачи с полями id, title, description, priority, created_at. 
        Если задача с указанным task_id не найдена, возвращается ошибка 404 Not Found.
    """,
    responses={
        200: {"description": "Успешный запрос"},
        404: {
            "description": "Задача не найдена",
            "content": {
                "application/json": {
                    "example": {"detail": {"detail": "Task not found", "task_id": 1}}
                }
            },
        },
    },
)
async def get_task(
    task_id: int = Path(..., description="Уникальный идентификатор задачи")
):
    """Получить задачу по её идентификатору."""

    # Ищем задачу в хранилище
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    # Если задача не найдена — возвращаем 404
    raise HTTPException(
        status_code=404, detail={"detail": "Task not found", "task_id": task_id}
    )
