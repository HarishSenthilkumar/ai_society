import random

JOBS = {
    "farmer": {
        "income": 8,
        "food": 5,
        "production": 4
    },
    "miner": {
        "income": 12,
        "food": 0,
        "production": 3
    },
    "builder": {
        "income": 15,
        "food": 0,
        "production": 1
    },
    "merchant": {
        "income": 11,
        "food": 1,
        "production": 1
    },
    "doctor": {
        "income": 20,
        "food": 0,
        "production": 0
    },
    "teacher": {
        "income": 14,
        "food": 1,
        "production": 0
    },
    "engineer": {
        "income": 22,
        "food": 0,
        "production": 2
    },
    "artist": {
        "income": 9,
        "food": 1,
        "production": 0
    },
    "unemployed": {
        "income": 3,
        "food": 0,
        "production": 0
    }
}

PERSONALITIES = [
    "ambitious",
    "generous",
    "social",
    "aggressive",
    "cautious",
    "balanced"
]
