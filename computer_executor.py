import json
import time
import pyautogui
import re

# -----------------------------
# SAFETY CONFIG
# -----------------------------
pyautogui.FAILSAFE = True   # Move mouse to top-left to abort
pyautogui.PAUSE = 0.1       # Small delay after each action

# -----------------------------
# DISPLAY CONFIG
# -----------------------------
VIRTUAL_WIDTH = 1000
VIRTUAL_HEIGHT = 1000

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


def virtual_to_screen(coord):
    """
    Convert 1000x1000 virtual coordinates
    to real screen pixel coordinates.
    """
    x, y = coord
    real_x = int(x / VIRTUAL_WIDTH * SCREEN_WIDTH)
    real_y = int(y / VIRTUAL_HEIGHT * SCREEN_HEIGHT)
    return real_x, real_y


def extract_tool_call(text):
    """
    Extract JSON from <tool_call>...</tool_call>
    """
    match = re.search(
        r"<tool_call>\s*(\{.*?\})\s*</tool_call>",
        text,
        re.DOTALL
    )
    if not match:
        raise ValueError("No <tool_call> block found")

    return json.loads(match.group(1))


def execute_computer_use(action_obj):
    """
    Execute the parsed computer_use action.
    """
    action = action_obj["arguments"]["action"]

    args = action_obj["arguments"]

    print(f"[EXECUTING] {action} -> {args}")

    # -----------------------------
    # MOUSE ACTIONS
    # -----------------------------
    if action == "mouse_move":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.moveTo(x, y)

    elif action == "left_click":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.click(x, y)

    elif action == "right_click":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.rightClick(x, y)

    elif action == "middle_click":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.middleClick(x, y)

    elif action == "double_click":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.doubleClick(x, y)

    elif action == "left_click_drag":
        x, y = virtual_to_screen(args["coordinate"])
        pyautogui.dragTo(x, y, duration=0.3, button="left")

    # -----------------------------
    # KEYBOARD ACTIONS
    # -----------------------------
    elif action == "type":
        pyautogui.write(args["text"], interval=0.02)

    elif action == "key":
        keys = []
        for k in args["keys"]:
            # Convert "win" to pyautogui-friendly key
            if k.lower() == "win":
                keys.append("winleft")
            else:
                keys.append(k.lower())
        pyautogui.hotkey(*keys)

    # -----------------------------
    # SCROLLING
    # -----------------------------
    elif action == "scroll" or action == "hscroll":
        pyautogui.scroll(int(args["pixels"]))

    # -----------------------------
    # WAIT
    # -----------------------------
    elif action == "wait":
        time.sleep(float(args["time"]))

    # -----------------------------
    # TERMINATE
    # -----------------------------
    elif action == "terminate":
        print(f"[TERMINATED] Status: {args.get('status')}")
        return "TERMINATED"

    # -----------------------------
    # ANSWER (NO ACTION)
    # -----------------------------
    elif action == "answer":
        print("[ANSWER]", args["text"])

    else:
        raise ValueError(f"Unknown action: {action}")


def run_tool_call(tool_call_text):
    """
    Main entry point.
    """
    tool_call = extract_tool_call(tool_call_text)

    if tool_call["name"] != "computer_use":
        raise ValueError("Unsupported function")

    return execute_computer_use(tool_call)
