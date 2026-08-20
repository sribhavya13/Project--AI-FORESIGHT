import re

def check_password_strength(password):
    """Check password strength"""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append("One uppercase letter")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append("One lowercase letter")

    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append("One number")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        feedback.append("One special character")

    if score >= 5:
        return "strong", "Strong password!", feedback
    elif score >= 3:
        return "medium", "Medium password", feedback
    else:
        return "weak", "Weak password", feedback

