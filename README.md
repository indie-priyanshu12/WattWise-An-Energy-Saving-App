# 💡 WattWise: Real-Time Energy Monitoring & Optimization App

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-orange.svg)](https://customtkinter.tomschimansky.com/)

**WattWise** is a comprehensive, production-ready desktop application designed to help users monitor, analyze, and optimize their electrical energy consumption. By providing **real-time insights** and **AI-powered recommendations**, WattWise empowers users to **lower their electricity bills** and make a tangible **contribution to environmental sustainability** by reducing their carbon footprint.

---

## 🎯 Core Purpose & Vision

Our goal is simple: to transform energy consumption from an invisible cost into a manageable, conscious habit.

* **⚡ Energy Awareness:** Gain real-time understanding of device-level electricity usage.
* **💰 Cost Reduction:** Identify and eliminate energy waste to significantly lower utility bills.
* **🌎 Environmental Impact:** Encourage sustainable practices that reduce overall carbon emissions.
* **🧠 Behavioral Change:** Foster energy-conscious decision-making through data visualization and friendly competition.

---

## ⬇️ Download & Installation

The easiest way to get started with WattWise is to download the latest executable file directly from our GitHub Releases page.

### Option 1: Direct Download (Recommended for Users)

Download the single-file executable package below, which includes all necessary dependencies.

| Platform | Download Link | Notes |
| :--- | :--- | :--- |
| **Windows (.exe)** | **[Download WattWise v1.0.0 for Windows](<YOUR_WINDOWS_EXECUTABLE_LINK_HERE>)** | *Self-contained executable (compiled via PyInstaller).* |
| **Source Code (.zip)** | **[Download WattWise v1.0.0 Source Code](<YOUR_SOURCE_CODE_ZIP_LINK_HERE>)** | *For Linux/Other Platforms or running from source.* |
| **All Releases** | **[View All Releases](<YOUR_GITHUB_RELEASES_PAGE_LINK_HERE>)** | *Find older versions or other platform builds.* |

> 📌 **NOTE:** You must replace all **`<PLACEHOLDERS_HERE>`** above with the actual links from your GitHub Release page after publishing your assets!

***

### Option 2: Run from Source (For Developers/Advanced Users)

If you prefer to run the application from the source code, follow these steps.

1.  **Clone the Repository (Requires Git):**
    ```bash
    git clone [https://github.com/yourusername/wattwise.git](https://github.com/yourusername/wattwise.git)
    cd wattwise
    ```

2.  **Install Dependencies (Requires Python 3.8+):**
    ```bash
    pip install customtkinter pandas matplotlib seaborn google-generativeai
    ```

3.  **Set up the Google API Key (Optional):**
    The AI recommendation feature requires your personal Google Gemini API Key. Set it as an environment variable before running:
    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```
    *(The app will prompt you if the key is not found).*

4.  **Run the Application:**
    ```bash
    python wattwise_app.py
    ```

---

## 🚀 Key Components & Features

WattWise is organized into a sleek, three-tab interface, providing a complete energy management solution.

### 1. 🏠 HOME (Main Tracking Tab)

The central control panel for real-time monitoring.

* **Real-Time Tracking:** Start/stop tracking for any device with a single **Toggle ON/OFF** button. Usage (in kWh) updates every second.
* **Device Management:** Easily add new devices by name and **Power Rating (Watts)**.
* **Total Usage Counter:** A running total of all active and saved usage.
* **AI Recommendations Box:** A dedicated area for receiving personalized, actionable energy-saving tips.

### 2. 📊 STATS (Analytics & Visualization)

Deep dive into your consumption patterns.

* **7-Day Usage Table:** An interactive table showing energy consumed (kWh) by **each device over the last 7 days**, helping you spot weekly trends.
* **Today's Consumption Pie Chart:** A visual, color-coded breakdown showing the **percentage of today's energy used by each device**, immediately highlighting high-consumption items.

### 3. 🏆 LEADERBOARD (Gamification & Comparison)

Motivate yourself through friendly competition.

* **Multi-User Ranking:** Scans local user data files to rank all users based on the **least total energy usage** (most efficient).
* **Visual Motivation:** Displays rank number, a **🥇 Gold Medal** for the top user, and a green highlight for the current user.

---

## 🤖 AI Integration (Google Gemini)

WattWise uses the **Google Generative AI (Gemini)** to provide personalized, intelligent advice based on your actual usage patterns.

* **Data Analysis:** The application securely sends your device list and historical usage logs to the Gemini model.
* **Actionable Tips:** The AI returns **3-5 personalized, bulleted energy-saving tips** tailored to your habits.
* *Example Recommendation:* "Refrigerator is running 24/7 - ensure door seals are tight or consider unplugging it when not in use during long trips."

---

## 🏗️ Technical Specifications

### Architecture & Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **GUI/Frontend** | **CustomTkinter** | Modern, sleek Python GUI framework (dark theme with #FFD369 accents). |
| **Core Logic** | **Python 3.8+** | Backend programming, calculation engine, and file I/O. |
| **Data Analysis** | **Pandas, Seaborn & Matplotlib** | Manipulation of logs and generating embedded charts. |
| **AI/ML** | **google-generativeai** | API access for the personalized recommendation engine. |

### Data Persistence Model

All data is stored **locally** in a transparent, plain text format, ensuring **privacy and control**.

* **File Format:** `[username]_data.txt`
* **Structure:** Divided into two clear sections: `DEVICES` (for names and power ratings) and `LOGS` (for all timestamped ON/OFF events).
* **Calculation:** Energy usage is calculated using the formula:
    $$\text{Units (kWh)} = \frac{\text{Power (W)} \times \text{Time (seconds)}}{3600 \times 1000}$$

---

## ⭐ Impact & Metrics

| Area | Potential Impact |
| :--- | :--- |
| **Cost Savings** | **10% - 25% Reduction** in monthly electricity bills by optimizing usage. |
| **Environmental** | Direct **reduction of your carbon footprint** through conscious energy demand reduction. |
| **Educational** | Increased understanding of energy consumption principles (Power vs. Energy). |

---

## 🤝 Contributing

Contributions are highly welcomed! Please feel free to fork the repository, create a feature branch, and open a Pull Request. Check the **Extensibility & Future Enhancements** section for ideas!
