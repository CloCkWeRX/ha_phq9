"""Constants for the PHQ-9 integration."""

DOMAIN = "phq9"

PHQ9_ANSWERS = [
    "Not at all",
    "Several days",
    "More than half the days",
    "Nearly every day",
]

SCORE_MAP = {answer: i for i, answer in enumerate(PHQ9_ANSWERS)}
