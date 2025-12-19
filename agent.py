# =====================================
# Autonomous Desktop Agent (PyAutoGUI)
# =====================================

import requests
import base64
import time
import os
import io
import re
from PIL import Image
import pyautogui

from computer_executor import run_tool_call

# -----------------------------
# CONFIG
# -----------------------------
SERVER_URL = "CLOUDFLARE_URL_ADD_HERE" 
ACT_ENDPOINT = f"{SERVER_URL}/act"


SCREENSHOT_DIR = "./client_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

MAX_REPEAT = 2
HISTORY_WINDOW = 5

pyautogui.FAILSAFE = True

# -----------------------------
# INIT
# -----------------------------
GOAL = input("Enter your desktop automation goal: ").strip()
if not GOAL:
    print("No goal provided. Exiting.")
    exit(1)

# semantic history (IMPORTANT)
stage2_history = []

last_actions = []

# -----------------------------
# UTILS
# -----------------------------
def take_screenshot() -> str:
    """
    Take screenshot, compress, return base64.
    """
    img = pyautogui.screenshot()
    img.thumbnail((1024, 1024))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)

    return base64.b64encode(buf.getvalue()).decode("utf-8")


def send_to_server(instruction: str, history: str, image_b64: str) -> dict:
    payload = {
        "instruction": instruction,
        "stage2_history": history,
        "image": image_b64,
    }

    try:
        resp = requests.post(ACT_ENDPOINT, json=payload, timeout=400)
        if resp.status_code == 200:
            return resp.json()
        print(f"Server error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Server connection failed: {e}")

    return {}


def sanitize_xml(text: str) -> str:
    return text.replace("```", "").strip()


def extract_signature(xml: str) -> str:
    """
    Used only for repeat detection.
    """
    match = re.search(r"<tool_call>.*?</tool_call>", xml, re.DOTALL)
    return match.group(0) if match else "invalid"


def extract_action_summary(model_output: str) -> str:
    """
    Extracts the Action: ... line for semantic history.
    """
    match = re.search(r"Action:\s*(.*)", model_output)
    return match.group(1).strip() if match else "Performed an action."


# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    step = 0

    while True:
        step += 1
        print(f"\n================ STEP {step} ================")

        # 1️⃣ Screenshot
        screenshot_b64 = take_screenshot()

        # 2️⃣ Prepare SHORT semantic history
        short_history = "\n".join(stage2_history[-HISTORY_WINDOW:])

        # 3️⃣ Ask server (Qwen)
        response = send_to_server(GOAL, short_history, screenshot_b64)

        if not response.get("success"):
            print("❌ Model failed. Retrying...")
            time.sleep(3)
            continue

        xml = sanitize_xml(response.get("xml", ""))
        raw = response.get("raw", "")

        print("\n[MODEL RAW OUTPUT]\n", raw)
        print("\n[TOOL CALL]\n", xml)

        # 🛑 TERMINATION
        if xml.lower() in ("<bye/>", "<terminate/>"):
            print("✅ Task completed.")
            break

        # 4️⃣ Repeat protection
        sig = extract_signature(xml)
        last_actions.append(sig)

        if last_actions[-MAX_REPEAT:].count(sig) >= MAX_REPEAT:
            print("⚠️ Repeated action detected. Waiting...")
            time.sleep(2)
            continue

        # 5️⃣ Execute action
        try:
            result = run_tool_call(xml)
            if result == "TERMINATED":
                print("✅ Execution terminated.")
                break
        except Exception as e:
            print(f"❌ Execution error: {e}")
            stage2_history.append("Execution failed.")
            continue

        # 6️⃣ Save SEMANTIC history
        action_summary = extract_action_summary(raw)
        stage2_history.append(action_summary)

        time.sleep(1)


if __name__ == "__main__":
    main()
