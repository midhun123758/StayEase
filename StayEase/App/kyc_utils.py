import os

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]
MAX_FILE_SIZE_MB = 5


def check_file_extension(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def check_file_size(file_size):
    max_size = MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size <= max_size


def calculate_fraud_score(file_name, file_size, extracted_name=None, submitted_name=None):
    score = 0
    reasons = []

    if not check_file_extension(file_name):
        score += 40
        reasons.append("Invalid file type")

    if not check_file_size(file_size):
        score += 30
        reasons.append("File size too large")

    if extracted_name and submitted_name:
        if extracted_name.lower().strip() != submitted_name.lower().strip():
            score += 40
            reasons.append("Name mismatch")

    return score, reasons