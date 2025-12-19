# Autonomous Desktop Agent using Qwen3-VL

A Python-based autonomous desktop agent that leverages **large vision-language models (LLMs)** to interact with a Windows desktop environment through GUI actions. This project allows a local computer to be controlled via LLM outputs without relying on external APIs, while using a **Colab notebook as a GPU-backed server**.

---

## 🚀 Overview

This project enables **Remote Computer Use** by leveraging a hybrid architecture:

* A powerful **Qwen3-VL Vision-Language Model** runs on a Google Colab GPU server.
* Your local laptop acts as the **client**, executing actions on your OS based on the model's **visual reasoning**.

---

## 🧩 System Architecture

The project overcomes the limitation of local hardware by offloading heavy computation to the cloud:

1. **Server (Google Colab)**

   * Hosts the **Flask API** and the **Qwen3-VL model**
   * Uses the **Colab GPU** to process screenshots and generate precise action coordinates

2. **Bridge (Cloudflare Tunnel)**

   * Provides a secure, high-speed, temporary link (`.trycloudflare.com`)
   * Bypasses firewalls to connect Colab to your laptop

3. **Client (Laptop)**

   * Runs the **agent loop**
   * Captures the current screen, sends it to the server, receives tool-call actions (click, type, scroll), and executes them locally

---

## 🧠 Model Specifications

* **Model Family:** Qwen3-VL (Vision-Language)
* **Optimized for testing:** Qwen3-VL-4B / 7B for low-latency experiments
* **Performance Scaling:** Accuracy in grounding (UI element detection) scales significantly with model size
* **Recommended for production:**

  * `Qwen/Qwen3-VL-235B-A22B-Thinking` for **complex reasoning** and **pixel-perfect accuracy**
* **Quantization Support:**

  * GPUs supporting **FP8** (like H100/A100) can use quantized versions to reduce VRAM usage while maintaining ~99% performance

---

## 🛠️ Project Structure

```
├── agent.py                 # The "Brain": feedback loop, screen capture, model interaction, and action triggering
├── computer_executor.py     # The "Hands": toolset for OS-level interactions (mouse, keyboard, app switching)
├── server.py                # Flask API running on Colab, hosting the Transformers Qwen3-VL model
├── requirements.txt         # Python dependencies
├── README.md
└── LICENSE                  # MIT license recommended
```

---

## 📈 Features

* Full control of desktop GUI using **LLM outputs**
* Feedback loop ensures continuous improvement of **action accuracy**
* Works **without external API calls**; uses **Transformers library**
* Ready-to-use tool functions in `computer_executor.py`
* `agent.py` handles sending screenshots and instructions, receiving outputs, executing actions, and maintaining the feedback loop

---

## 🚧 Limitations & Solutions

### The Bounding Box Challenge

**Problem:**

* Smaller models (4B/7B) occasionally struggle with **grounding**—pinpointing exact `(x, y)` coordinates of small app icons or UI buttons

**Solution:**

* Upgrade to **larger models** in the Qwen3-VL family (e.g., 235B)
* Larger models significantly improve **spatial awareness**, enabling precise interactions even on high-resolution displays and dense UI layouts

---

## 🔗 Server Setup

1. Run the **Flask server** on Colab
2. Expose it using **Cloudflare Tunnel** to get a public URL
3. Set the public URL in your local agent script:

```python
SERVER_URL = "https://your-cloudflare-tunnel-link.trycloudflare.com"
ACT_ENDPOINT = f"{SERVER_URL}/act"
```

This setup allows you to **leverage Colab GPU** while controlling your laptop locally.

---

## 📖 References

* [Qwen3-VL Computer Use Cookbook](https://colab.research.google.com/github/QwenLM/Qwen3-VL/blob/main/cookbooks/computer_use.ipynb#scrollTo=753a1d0c)
