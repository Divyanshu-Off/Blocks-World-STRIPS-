class STRIPS:
    def __init__(self):
        # Define operators (actions) with preconditions and effects
        self.operators = [
            ("pick_up", lambda s, b: b in s["clear"] and b in s["ontable"], lambda s, b: self.update_state(s, "pick_up", b)),
            ("put_down", lambda s, b: b in s["holding"], lambda s, b: self.update_state(s, "put_down", b)),
            ("stack", lambda s, b, x: b in s["holding"] and x in s["clear"] and (x in s["ontable"] or any(y == x for _, y in s["on"])), lambda s, b, x: self.update_state(s, "stack", b, x)),
            ("unstack", lambda s, b, x: (b, x) in s["on"] and b in s["clear"], lambda s, b, x: self.update_state(s, "unstack", b, x))
        ]

    def update_state(self, state, action, b, x=None):
        """ Updates the state based on the action performed."""
        new_state = {key: set(val) for key, val in state.items()}  # Create a copy of the state
        
        if action == "pick_up":
            # Pick up a block from the table
            new_state["holding"].add(b)
            new_state["clear"].remove(b)
            new_state["ontable"].remove(b)
        elif action == "put_down":
            # Put down a block onto the table
            new_state["holding"].remove(b)
            new_state["clear"].add(b)
            new_state["ontable"].add(b)
        elif action == "stack":
            # Stack a block on top of another block
            new_state["holding"].remove(b)
            new_state["clear"].remove(x)
            new_state["on"].add((b, x))
        elif action == "unstack":
            # Unstack a block from another block
            new_state["holding"].add(b)
            new_state["clear"].add(x)
            new_state["on"].remove((b, x))
        
        return new_state

    def plan(self, state, goal):
        """ Generates a plan to reach the goal state."""
        plan = []  # Stores the sequence of actions
        visited = set()  # Tracks visited states to prevent infinite loops
        
        while state != goal:
            state_tuple = tuple(sorted(state["on"]))  # Convert 'on' state to a tuple for comparison
            if state_tuple in visited:
                break  # Avoid infinite loops
            visited.add(state_tuple)
            
            for name, precond, effect in self.operators:
                if name in ["pick_up", "put_down"]:
                    # Apply pick_up or put_down actions
                    for b in list(state["clear"]):
                        if precond(state, b):
                            state = effect(state, b)
                            plan.append((name, b))
                            break
                elif name in ["stack", "unstack"]:
                    # Apply stack or unstack actions
                    for b, x in list(state["on"]):
                        if precond(state, b, x):
                            state = effect(state, b, x)
                            plan.append((name, b, x))
                            break
        
        return plan

# User input for blocks
blocks = []
print("Enter block names (max 4). Type 'done' to finish:")
while len(blocks) < 4:
    block = input(f"Block {len(blocks) + 1}: ").strip()
    if block.lower() == "done":
        break
    if block and block not in blocks:
        blocks.append(block)

# Default blocks if the user provides no input
if not blocks:
    blocks = ["A", "B", "C", "D"][:4]

# Initial state: all blocks are on the table and clear
initial_state = {"clear": set(blocks), "ontable": set(blocks), "holding": set(), "on": set()}

# Goal state: Blocks arranged in reverse order (stacked)
goal_stack = blocks[::-1]  # Reverse order for goal stack
goal_state = {"clear": {goal_stack[-1]}, "ontable": {goal_stack[0]}, "holding": set(), "on": {(goal_stack[i+1], goal_stack[i]) for i in range(len(goal_stack)-1)}}

# Create a planner instance and generate the plan
planner = STRIPS()
plan = planner.plan(initial_state, goal_state)

# Display the sequence of actions to arrange the blocks
print("\nPlan to arrange blocks:")
for step in plan:
    print(step)

# Display the final stacked order
print("\nFinal arranged blocks (top to bottom):", " -> ".join(goal_stack))
