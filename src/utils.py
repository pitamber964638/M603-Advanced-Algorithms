
import json


def load_constraints(file_path):
    """
    Loads the scheduling problem data from a JSON file.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def validate_constraints(data):
    """
    Checks whether the input data has the required structure.
    Returns a list of validation messages.
    """
    messages = []

    required_keys = ["classes", "rooms", "student_groups", "time_slots"]

    for key in required_keys:
        if key not in data:
            messages.append(f"Missing required key: {key}")

    if messages:
        return messages

    class_ids = [c["id"] for c in data["classes"]]
    room_ids = [r["id"] for r in data["rooms"]]

    # Check duplicate class IDs
    if len(class_ids) != len(set(class_ids)):
        messages.append("Duplicate class IDs found.")
    else:
        messages.append("Class IDs are unique.")

    # Check duplicate room IDs
    if len(room_ids) != len(set(room_ids)):
        messages.append("Duplicate room IDs found.")
    else:
        messages.append("Room IDs are unique.")

    # Check class fields
    for c in data["classes"]:
        if "id" not in c or "students" not in c or "professor" not in c:
            messages.append(f"Class has missing fields: {c}")
        elif c["students"] <= 0:
            messages.append(f"Invalid student number in class: {c['id']}")

    # Check room fields
    for r in data["rooms"]:
        if "id" not in r or "capacity" not in r:
            messages.append(f"Room has missing fields: {r}")
        elif r["capacity"] <= 0:
            messages.append(f"Invalid room capacity in room: {r['id']}")

    # Check student group class references
    for group, assigned_classes in data["student_groups"].items():
        for class_id in assigned_classes:
            if class_id not in class_ids:
                messages.append(
                    f"Student group {group} refers to unknown class: {class_id}"
                )

    # Check time slots
    if len(data["time_slots"]) == 0:
        messages.append("No time slots provided.")
    else:
        messages.append("Time slots are available.")

    if len(messages) == 3:
        messages.append("Input data validation passed.")

    return messages


def get_class_by_id(data):
    """
    Creates a dictionary for quick access to class information by class ID.
    """
    return {c["id"]: c for c in data["classes"]}


def get_room_by_id(data):
    """
    Creates a dictionary for quick access to room information by room ID.
    """
    return {r["id"]: r for r in data["rooms"]}
