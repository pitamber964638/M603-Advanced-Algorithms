
from src.greedy_solver import build_class_group_map, calculate_total_waste


def count_hard_conflicts(schedule, data):
    """
    Counts hard constraint violations in a produced schedule.

    Hard constraints checked:
    1. Same room cannot be used twice in the same time slot.
    2. Same professor cannot teach two classes in the same time slot.
    3. Same student group cannot attend two classes in the same time slot.
    4. Class must fit inside assigned room.
    """
    conflicts = 0
    class_to_groups = build_class_group_map(data["student_groups"])

    # Capacity conflicts
    for item in schedule:
        if item["students"] > item["room_capacity"]:
            conflicts += 1

    # Pairwise room, professor, and student group conflicts
    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            a = schedule[i]
            b = schedule[j]

            if a["time_slot"] != b["time_slot"]:
                continue

            # Room double-booking
            if a["room_id"] == b["room_id"]:
                conflicts += 1

            # Professor conflict
            if a["professor"] == b["professor"]:
                conflicts += 1

            # Student group conflict
            groups_a = set(class_to_groups.get(a["class_id"], []))
            groups_b = set(class_to_groups.get(b["class_id"], []))

            if groups_a.intersection(groups_b):
                conflicts += 1

    return conflicts


def evaluate_schedule(name, schedule, unscheduled, data):
    """
    Returns the main evaluation metrics for one scheduling method.
    """
    return {
        "method": name,
        "scheduled_classes": len(schedule),
        "unscheduled_classes": len(unscheduled),
        "hard_conflicts": count_hard_conflicts(schedule, data),
        "total_wasted_seats": calculate_total_waste(schedule)
    }


def print_comparison_table(results):
    """
    Prints a simple comparison table for report screenshots.
    """
    print("FINAL ALGORITHM COMPARISON")
    print("-" * 90)
    print(
        f"{'Method':<35} "
        f"{'Scheduled':<12} "
        f"{'Unscheduled':<14} "
        f"{'Conflicts':<12} "
        f"{'Room Waste':<12}"
    )
    print("-" * 90)

    for result in results:
        print(
            f"{result['method']:<35} "
            f"{result['scheduled_classes']:<12} "
            f"{result['unscheduled_classes']:<14} "
            f"{result['hard_conflicts']:<12} "
            f"{result['total_wasted_seats']:<12}"
        )

    print("-" * 90)
