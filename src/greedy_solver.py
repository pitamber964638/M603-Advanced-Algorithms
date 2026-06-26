
def build_class_group_map(student_groups):
    """
    Creates a reverse mapping:
    class_id -> list of student groups that attend the class
    """
    class_to_groups = {}

    for group, class_list in student_groups.items():
        for class_id in class_list:
            if class_id not in class_to_groups:
                class_to_groups[class_id] = []
            class_to_groups[class_id].append(group)

    return class_to_groups


def has_professor_conflict(schedule, class_info, time_slot):
    """
    Checks whether the same professor is already teaching
    another class in the selected time slot.
    """
    for assigned in schedule:
        if assigned["time_slot"] == time_slot:
            if assigned["professor"] == class_info["professor"]:
                return True
    return False


def has_student_group_conflict(schedule, class_info, time_slot, class_to_groups):
    """
    Checks whether any student group already has another class
    in the selected time slot.
    """
    current_groups = set(class_to_groups.get(class_info["id"], []))

    for assigned in schedule:
        if assigned["time_slot"] == time_slot:
            assigned_groups = set(class_to_groups.get(assigned["class_id"], []))

            if current_groups.intersection(assigned_groups):
                return True

    return False


def has_room_conflict(schedule, room, time_slot):
    """
    Checks whether a room is already booked in the selected time slot.
    """
    for assigned in schedule:
        if assigned["time_slot"] == time_slot and assigned["room_id"] == room["id"]:
            return True
    return False


def greedy_schedule(data):
    """
    Greedy baseline scheduler.

    Logic:
    1. Sort classes by number of students in descending order.
    2. Try each time slot and room in order.
    3. Assign the first feasible room and time slot.
    4. If no valid assignment exists, mark the class as unscheduled.
    """
    classes = sorted(data["classes"], key=lambda x: x["students"], reverse=True)
    rooms = data["rooms"]  # First-fit baseline uses original room order
    time_slots = data["time_slots"]

    class_to_groups = build_class_group_map(data["student_groups"])

    schedule = []
    unscheduled = []

    for class_info in classes:
        placed = False

        for time_slot in time_slots:
            for room in rooms:

                # Room must be large enough
                if room["capacity"] < class_info["students"]:
                    continue

                # Hard constraints
                if has_professor_conflict(schedule, class_info, time_slot):
                    continue

                if has_student_group_conflict(schedule, class_info, time_slot, class_to_groups):
                    continue

                if has_room_conflict(schedule, room, time_slot):
                    continue

                wasted_seats = room["capacity"] - class_info["students"]

                schedule.append({
                    "class_id": class_info["id"],
                    "professor": class_info["professor"],
                    "students": class_info["students"],
                    "time_slot": time_slot,
                    "room_id": room["id"],
                    "room_capacity": room["capacity"],
                    "wasted_seats": wasted_seats,
                    "method": "Greedy"
                })

                placed = True
                break

            if placed:
                break

        if not placed:
            unscheduled.append({
                "class_id": class_info["id"],
                "students": class_info["students"],
                "professor": class_info["professor"],
                "reason": "No feasible time slot and room found under hard constraints"
            })

    return schedule, unscheduled


def calculate_total_waste(schedule):
    """
    Calculates total wasted room capacity.
    """
    return sum(item["wasted_seats"] for item in schedule)


def print_schedule(schedule, unscheduled):
    """
    Prints the schedule in the required conflict-report style.
    """
    print("GREEDY BASELINE OUTPUT")
    print("-" * 70)

    for item in schedule:
        if item["wasted_seats"] == 0:
            fit_status = "Perfect Fit"
        else:
            fit_status = f"Wasted {item['wasted_seats']} seats"

        print(
            f"Scheduled {item['class_id']} | "
            f"{item['time_slot']} | "
            f"{item['room_id']} | "
            f"{fit_status}"
        )

    for item in unscheduled:
        print(
            f"Unscheduled {item['class_id']} | "
            f"N/A | N/A | "
            f"Reason: {item['reason']}"
        )

    print("-" * 70)
    print("Scheduled classes:", len(schedule))
    print("Unscheduled classes:", len(unscheduled))
    print("Total wasted seats:", calculate_total_waste(schedule))
