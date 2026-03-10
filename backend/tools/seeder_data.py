from app.models.user import User, UserRole
SEED_USERS = [
    {
        "email": "admin@example.com",
        "username": "admin",
        "password": "Asdqwe123@",
        "role": UserRole.APPROVER,
    },
    {
        "email": "verifier@example.com",
        "username": "verifier",
        "password": "Asdqwe123@",
        "role": UserRole.VERIFIER,
    },
    {
        "email": "user@example.com",
        "username": "user",
        "password": "Asdqwe123@",
        "role": UserRole.USER,
    },
    {
        "email": "user2@example.com",
        "username": "user2",
        "password": "Asdqwe123@",
        "role": UserRole.USER,
    },
]

SEED_INSURANCES = [
    {
        "number": "INS-2024-001",
        "title": "Health Insurance Basic",
        "description": "Basic health insurance coverage for individuals",
    },
    {
        "number": "INS-2024-002",
        "title": "Health Insurance Premium",
        "description": "Comprehensive health insurance with dental and vision coverage",
    },
    {
        "number": "INS-2024-003",
        "title": "Vehicle Insurance",
        "description": "Full coverage vehicle insurance including collision and theft protection",
    },
    {
        "number": "INS-2024-004",
        "title": "Property Insurance",
        "description": "Home and property insurance covering fire, flood, and natural disasters",
    },
    {
        "number": "INS-2024-005",
        "title": "Life Insurance",
        "description": "Term life insurance with flexible coverage options",
    },
]

