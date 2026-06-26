
from src.greedy_solver import build_class_group_map, calculate_total_waste
from src.graph_engine import build_conflict_graph


def backtracking_schedule(data, max_search_nodes=200000):
    """
    Recursive backtracking scheduler.

    Goal:
    1. Schedule as many classes as possible.
    2. Avoid professor conflicts, student group conflicts, and room double-booking.
    3. Use suitable rooms only.
    4. Among schedules with the same number of classes, prefer lower wasted seats.

    Best-effort strategy:
    If a full schedule cannot be found, the best partial schedule is returned and
    unscheduled classes are clearly flagged for manual intervention.

    Pruning strategy:
    1. If the current branch cannot beat the best number of scheduled classes, stop.
    2. If scheduled count is equal to the best but already has higher waste, stop.
    3. Invalid professor, student group, room, and capacity combinations are skipped early.
    """

    classes = data["classes"]
    rooms = sorted(data["rooms"], key=lambda r: r["capacity"])
    time_slots = data["time_slots"]

    class_to_groups = build_class_group_map(data["student_groups"])
    conflict_graph = build_conflict_graph(data)

    # Most constrained and larger classes are attempted first
    ordered_classes = sorted(
        classes,
        key=lambda c: (len(conflict_graph[c["id"]]), c["students"]),
        reverse=True
    )

    best_schedule = []
    best_waste = float("inf")
    search_nodes = 0

    # Fast lookup sets for constraints
    used_rooms_by_slot = {slot: set() for slot in time_slots}
    used_professors_by_slot = {slot: set() for slot in time_slots}
    used_groups_by_slot = {slot: set() for slot in time_slots}

    current_schedule = []

    def is_valid_assignment(class_info, room, time_slot):
        """
        Checks whether assigning a class to a room and time slot is valid.
        """
        if room["capacity"] < class_info["students"]:
            return False

        if room["id"] in used_rooms_by_slot[time_slot]:
            return False

        if class_info["professor"] in used_professors_by_slot[time_slot]:
            return False

        class_groups = set(class_to_groups.get(class_info["id"], []))
        if class_groups.intersection(used_groups_by_slot[time_slot]):
            return False

        return True

    def place_class(class_info, room, time_slot):
        """
        Applies an assignment.
        """
        waste = room["capacity"] - class_info["students"]

        item = {
            "class_id": class_info["id"],
            "professor": class_info["professor"],
            "students": class_info["students"],
            "time_slot": time_slot,
            "room_id": room["id"],
            "room_capacity": room["capacity"],
            "wasted_seats": waste,
            "method": "Backtracking"
        }

        current_schedule.append(item)
        used_rooms_by_slot[time_slot].add(room["id"])
        used_professors_by_slot[time_slot].add(class_info["professor"])

        for group in class_to_groups.get(class_info["id"], []):
            used_groups_by_slot[time_slot].add(group)

        return item

    def remove_class(item):
        """
        Undoes an assignment during backtracking.
        """
        current_schedule.pop()

        time_slot = item["time_slot"]
        class_id = item["class_id"]
        professor = item["professor"]
        room_id = item["room_id"]

        used_rooms_by_slot[time_slot].remove(room_id)
        used_professors_by_slot[time_slot].remove(professor)

        for group in class_to_groups.get(class_id, []):
            used_groups_by_slot[time_slot].remove(group)

    def recursive_search(index):
        nonlocal best_schedule, best_waste, search_nodes

        search_nodes += 1

        # Safety limit for larger datasets
        if search_nodes > max_search_nodes:
            return

        current_count = len(current_schedule)
        current_waste = calculate_total_waste(current_schedule)
        remaining = len(ordered_classes) - index

        # Prune branches that cannot improve the best scheduled count
        if current_count + remaining < len(best_schedule):
            return

        # Prune branches with same count but already worse waste
        if current_count + remaining == len(best_schedule) and current_waste >= best_waste:
            return

        # Update best solution
        if current_count > len(best_schedule):
            best_schedule = [item.copy() for item in current_schedule]
            best_waste = current_waste
        elif current_count == len(best_schedule) and current_waste < best_waste:
            best_schedule = [item.copy() for item in current_schedule]
            best_waste = current_waste

        # Stop if all classes have been considered
        if index == len(ordered_classes):
            return

        class_info = ordered_classes[index]

        # Try feasible assignments first
        for time_slot in time_slots:
            for room in rooms:
                if is_valid_assignment(class_info, room, time_slot):
                    item = place_class(class_info, room, time_slot)
                    recursive_search(index + 1)
                    remove_class(item)

        # Best-effort branch: allow this class to remain unscheduled
        recursive_search(index + 1)

    recursive_search(0)

    scheduled_ids = {item["class_id"] for item in best_schedule}
    unscheduled = []

    for class_info in classes:
        if class_info["id"] not in scheduled_ids:
            unscheduled.append({
                "class_id": class_info["id"],
                "students": class_info["students"],
                "professor": class_info["professor"],
                "reason": "Could not be placed without violating hard constraints"
            })

    return best_schedule, unscheduled, search_nodes


def print_backtracking_schedule(schedule, unscheduled, search_nodes):
    """
    Prints final backtracking schedule and conflict report.
    """
    print("BACKTRACKING BEST-EFFORT OUTPUT")
    print("-" * 70)

    for item in sorted(schedule, key=lambda x: (x["time_slot"], x["room_id"])):
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
    print("Search nodes explored:", search_nodes)

    print("\nCONFLICT REPORT")
    print("-" * 70)
    if len(unscheduled) == 0:
        print("No unscheduled classes. Manual intervention is not required.")
    else:
        for item in unscheduled:
            print(
                f"{item['class_id']} requires manual intervention. "
                f"Reason: {item['reason']}"
            )
