
from functools import lru_cache
from collections import defaultdict
from src.greedy_solver import calculate_total_waste
from src.graph_engine import (
    build_conflict_graph,
    welsh_powell_coloring,
    assign_time_slots_from_coloring
)


def optimise_rooms_for_single_time_slot(class_ids, class_lookup, rooms):
    """
    Uses Dynamic Programming with bitmasking to assign classes to rooms.

    DP State:
        dp(i, used_rooms_mask)

    Meaning:
        Minimum wasted room capacity after assigning rooms to classes
        from index i onward, given the set of rooms already used.

    Recurrence:
        dp(i, mask) = min(
            room_capacity - class_students + dp(i + 1, mask with selected room)
        )

    Base case:
        If all classes are assigned, waste = 0.

    This avoids checking invalid repeated-room combinations directly.
    """

    # Larger classes are considered first because they have fewer feasible room options
    class_ids = sorted(
        class_ids,
        key=lambda cid: class_lookup[cid]["students"],
        reverse=True
    )

    @lru_cache(None)
    def dp(index, used_mask):
        if index == len(class_ids):
            return 0, []

        current_class_id = class_ids[index]
        current_class = class_lookup[current_class_id]
        students = current_class["students"]

        best_waste = float("inf")
        best_assignment = None

        for room_index, room in enumerate(rooms):

            # Skip already used rooms
            if used_mask & (1 << room_index):
                continue

            # Room must fit class size
            if room["capacity"] < students:
                continue

            waste = room["capacity"] - students

            next_waste, next_assignment = dp(
                index + 1,
                used_mask | (1 << room_index)
            )

            total_waste = waste + next_waste

            if total_waste < best_waste:
                best_waste = total_waste
                best_assignment = [
                    {
                        "class_id": current_class_id,
                        "professor": current_class["professor"],
                        "students": current_class["students"],
                        "room_id": room["id"],
                        "room_capacity": room["capacity"],
                        "wasted_seats": waste,
                        "method": "Graph Coloring + DP"
                    }
                ] + next_assignment

        return best_waste, best_assignment

    minimum_waste, assignment = dp(0, 0)

    if assignment is None:
        return None, float("inf")

    return assignment, minimum_waste


def dp_room_optimised_schedule(data):
    """
    Full Stage 3 process:
    1. Build conflict graph.
    2. Use Welsh-Powell graph coloring to fix safe time slots.
    3. Apply DP room optimisation separately for each time slot.
    """

    graph = build_conflict_graph(data)
    coloring = welsh_powell_coloring(graph)
    time_assignment, time_unscheduled = assign_time_slots_from_coloring(data, coloring)

    class_lookup = {c["id"]: c for c in data["classes"]}

    # Rooms are sorted only for stable output.
    # DP still checks all feasible room combinations.
    rooms = sorted(data["rooms"], key=lambda room: room["capacity"], reverse=True)

    classes_by_slot = defaultdict(list)

    for class_id, time_slot in time_assignment.items():
        classes_by_slot[time_slot].append(class_id)

    final_schedule = []
    unscheduled = list(time_unscheduled)

    for time_slot, class_ids in classes_by_slot.items():
        assignment, waste = optimise_rooms_for_single_time_slot(
            class_ids,
            class_lookup,
            rooms
        )

        if assignment is None:
            for class_id in class_ids:
                class_info = class_lookup[class_id]
                unscheduled.append({
                    "class_id": class_id,
                    "students": class_info["students"],
                    "professor": class_info["professor"],
                    "reason": "DP could not find feasible room allocation for this time slot"
                })
        else:
            for item in assignment:
                item["time_slot"] = time_slot
                final_schedule.append(item)

    return final_schedule, unscheduled


def print_dp_schedule(schedule, unscheduled):
    """
    Prints the DP optimised schedule.
    """
    print("DYNAMIC PROGRAMMING ROOM OPTIMISATION OUTPUT")
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


def compare_stage_results(greedy_schedule, graph_schedule, dp_schedule):
    """
    Compares waste across the first three project stages.
    """
    print("\nSTAGE COMPARISON")
    print("-" * 70)
    print(f"Greedy baseline total waste: {calculate_total_waste(greedy_schedule)}")
    print(f"Graph coloring with simple room assignment total waste: {calculate_total_waste(graph_schedule)}")
    print(f"Graph coloring with DP room optimisation total waste: {calculate_total_waste(dp_schedule)}")
    print("-" * 70)
