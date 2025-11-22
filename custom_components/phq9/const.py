"""Constants for the PHQ-9 integration."""

DOMAIN = "phq9"

PHQ9_ANSWER_KEYS = [
    "not_at_all",
    "several_days",
    "more_than_half_the_days",
    "nearly_every_day",
]

DIFFICULTY_ANSWER_KEYS = [
    "not_difficult_at_all",
    "somewhat_difficult",
    "very_difficult",
    "extremely_difficult",
]

SCORE_MAP = {answer_key: i for i, answer_key in enumerate(PHQ9_ANSWER_KEYS)}
