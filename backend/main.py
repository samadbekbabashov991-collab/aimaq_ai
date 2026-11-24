from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="AIMAQ AI API",
    description="Жергілікті мәселелерді анықтау, талдау және бақылау платформасының MVP API прототипі",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReportCreate(BaseModel):
    location: str
    description: str
    category: Optional[str] = None
    has_photo: bool = False


class IssueCluster(BaseModel):
    id: str
    location: str
    category: str
    description: str
    count: int
    priority: str
    status: str
    ai_reason: str


clusters_db: List[IssueCluster] = [
    IssueCluster(
        id="REQ-101",
        location="Абай көшесі, 112",
        category="Жол инфрақұрылымы",
        description="Жол бетіндегі терең шұңқыр және жиектастың бұзылуы",
        count=4,
        priority="Жоғары",
        status="Жаңа / AI талдады",
        ai_reason="Бір локациядан 4 қайталанатын хабарлама біріктірілді.",
    )
]


def classify_text(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["шұңқыр", "жол", "асфальт", "яма"]):
        return "Жол инфрақұрылымы"
    if any(k in t for k in ["жарық", "шам", "свет", "фонар"]):
        return "Көше жарығы"
    if any(k in t for k in ["қоқыс", "мусор", "тазалық"]):
        return "Тазалық және қоқыс"
    return "Су құбыры / ТКШ"


@app.get("/")
def health_check():
    return {"status": "ok", "project": "AIMAQ AI MVP"}


@app.get("/api/issues", response_model=List[IssueCluster])
def list_issues():
    return clusters_db


@app.post("/api/reports", response_model=IssueCluster)
def submit_report(report: ReportCreate):
    category = report.category or classify_text(report.description)
    for item in clusters_db:
        if item.category == category and report.location.lower()[:10] in item.location.lower():
            item.count += 1
            if item.count >= 3:
                item.priority = "Жоғары"
            item.ai_reason = f"Бір локациядан {item.count} ұқсас өтініш біріктірілді."
            return item

    new_item = IssueCluster(
        id=f"REQ-{101 + len(clusters_db)}",
        location=report.location,
        category=category,
        description=report.description,
        count=1,
        priority="Орташа",
        status="Жаңа / AI талдады",
        ai_reason=f"NLP модулі өтінішті «{category}» санатына жіктеді.",
    )
    clusters_db.insert(0, new_item)
    return new_item
