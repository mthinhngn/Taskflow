import logging
from datetime import datetime
from typing import List
import json

from openai import OpenAI, APIError

from app.config import get_settings
from app.schemas import TaskForPrioritization, PrioritizationResult

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OpenAI client if API key provided
openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def calculate_deadline_urgency(due_at: datetime | None) -> float:
    """
    Calculate deadline urgency score (0-1).
    Higher score = more urgent.
    """
    if due_at is None:
        return 0.1

    now = datetime.utcnow()
    if due_at <= now:
        return 1.0  # Overdue

    hours_until_due = (due_at - now).total_seconds() / 3600

    if hours_until_due < 1:
        return 0.95
    elif hours_until_due < 6:
        return 0.80
    elif hours_until_due < 24:
        return 0.60
    elif hours_until_due < 72:
        return 0.40
    else:
        return 0.20


def calculate_effort_inverse(estimated_minutes: int | None) -> float:
    """
    Calculate effort inverse (0-1).
    Quick tasks (high score), long tasks (low score).
    """
    if estimated_minutes is None:
        return 0.5

    if estimated_minutes <= 15:
        return 0.95
    elif estimated_minutes <= 30:
        return 0.85
    elif estimated_minutes <= 60:
        return 0.70
    elif estimated_minutes <= 120:
        return 0.50
    else:
        return 0.30


def rule_based_score(task: TaskForPrioritization) -> float:
    """
    Calculate task priority score using rule-based heuristic.
    Combines: deadline urgency, importance, and effort inverse.
    Returns score in [0, 1].
    """
    deadline_urgency = calculate_deadline_urgency(task.due_at)
    importance_norm = task.importance / 5.0  # Normalize to 0-1
    effort_inverse = calculate_effort_inverse(task.estimated_minutes)

    # Weighted combination
    score = (
        0.5 * deadline_urgency +
        0.3 * importance_norm +
        0.2 * effort_inverse
    )

    return min(1.0, max(0.0, score))


def generate_rule_based_rationale(task: TaskForPrioritization) -> str:
    """Generate a rule-based rationale for task prioritization."""
    factors = []

    # Deadline
    if task.due_at:
        now = datetime.utcnow()
        hours_until = (task.due_at - now).total_seconds() / 3600
        if hours_until < 0:
            factors.append("overdue")
        elif hours_until < 24:
            factors.append("imminent deadline")
        elif hours_until < 72:
            factors.append("due soon")

    # Importance
    if task.importance >= 4:
        factors.append("high importance")
    elif task.importance == 1:
        factors.append("low priority")

    # Effort
    if task.estimated_minutes and task.estimated_minutes <= 30:
        factors.append("quick win")
    elif task.estimated_minutes and task.estimated_minutes > 120:
        factors.append("significant effort")

    if not factors:
        factors.append("standard priority")

    return "; ".join(factors) + "."


def prioritize_with_openai(tasks: List[TaskForPrioritization]) -> tuple[List[PrioritizationResult], List[str]]:
    """
    Use OpenAI GPT-4 to prioritize tasks and generate a daily plan.
    Falls back to rule-based if API fails.
    """
    if not openai_client or settings.ai_provider != "openai":
        return prioritize_rule_based(tasks)

    try:
        # Build task list for the prompt
        task_descriptions = "\n".join([
            f"- {i+1}. {task.title} (due: {task.due_at or 'no deadline'}, "
            f"effort: {task.estimated_minutes or 'unknown'} min, importance: {task.importance}/5)"
            for i, task in enumerate(tasks)
        ])

        prompt = f"""You are a productivity expert. Given the following tasks, prioritize them and generate a daily plan.

Tasks:
{task_descriptions}

For each task, provide:
1. A priority score (0.0-1.0)
2. A brief rationale

Then, generate a realistic daily plan with time slots.

Respond ONLY with a valid JSON object (no markdown, no extra text):
{{
  "results": [
    {{"title": "task title", "score": 0.95, "rationale": "reason"}},
    ...
  ],
  "plan": ["09:00-10:30 Task 1", "10:45-11:15 Task 2", ...]
}}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        response_text = response.choices[0].message.content.strip()

        # Parse JSON response
        data = json.loads(response_text)
        results = [PrioritizationResult(**r) for r in data["results"]]
        plan = data["plan"]

        logger.info(f"OpenAI prioritization succeeded for {len(tasks)} tasks")
        return results, plan

    except (APIError, ValueError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"OpenAI prioritization failed: {e}. Falling back to rule-based.")
        return prioritize_rule_based(tasks)


def prioritize_rule_based(tasks: List[TaskForPrioritization]) -> tuple[List[PrioritizationResult], List[str]]:
    """
    Prioritize tasks using rule-based heuristic (no external API).
    """
    results = []
    for task in tasks:
        score = rule_based_score(task)
        rationale = generate_rule_based_rationale(task)
        results.append(PrioritizationResult(title=task.title, score=score, rationale=rationale))

    # Sort by score descending
    results.sort(key=lambda x: x.score, reverse=True)

    # Generate simple daily plan from top tasks
    plan = []
    current_hour = 9  # Start at 9 AM
    for i, result in enumerate(results[:5]):  # Plan top 5 tasks
        # Find original task to get estimated time
        orig_task = next((t for t in tasks if t.title == result.title), None)
        duration = orig_task.estimated_minutes // 60 if orig_task and orig_task.estimated_minutes else 1
        end_hour = min(current_hour + duration, 18)  # Don't go past 6 PM
        plan.append(f"{current_hour:02d}:00-{end_hour:02d}:00 {result.title}")
        current_hour = end_hour + 1  # 1 hour break

    return results, plan


def prioritize_tasks(tasks: List[TaskForPrioritization]) -> tuple[List[PrioritizationResult], List[str]]:
    """
    Main function to prioritize tasks.
    Delegates to OpenAI or rule-based depending on settings.
    """
    if settings.ai_provider == "openai" and openai_client:
        return prioritize_with_openai(tasks)
    else:
        return prioritize_rule_based(tasks)
