# ⚡ AI-Driven Real-Time Battery SOC Estimation with Intelligent Power Control

A machine learning system that estimates the **State of Charge (SOC)** of batteries in real time using live sensor data from an Arduino, a trained Random Forest model, and an ESP32-based relay for intelligent power control.

---

## 📌 Project Overview

This project addresses the challenge of accurately estimating battery SOC — a critical parameter in battery management systems (BMS). Instead of traditional coulomb counting or voltage-lookup methods, this system uses a **Random Forest Regressor** trained on real discharge data to predict SOC from live sensor readings (voltage, current, temperature, and time).

The system supports **multiple battery chemistries** (Li-Ion, LFP, NiMH, SLA 12V, SLA 24V), provides a **live web dashboard**, logs all predictions to Excel, and serves a JSON feed that an ESP32 can poll to trigger protective relay actions.

---

## 🗂️ Project Structure

```
SOC_ML_Project/
│
├── BATTERY.py                        # Script 1 — Model training pipeline
├── new.py                            # Script 2 — Live prediction & control system
├── battery_soc_sensor.ino            # Arduino firmware — sensor data acquisition
├── 24V_LFP_Discharge_Training.csv    # Training dataset (24V LFP discharge cycle)
├── Picture2.jpg                      # Project diagram / reference image
└── Picture7.png                      # Project diagram / reference image
```

---

## 🧠 How It Works

```
Arduino Sensors  →  Serial (USB)  →  new.py (ML Prediction)  →  soc_feed.json
 (V, I, T, t)                         Random Forest Model          ↓
                                          ↓                    ESP32 polls feed
                                     Excel Log                 → Relay ON/OFF
                                          ↓
                                     Live Dashboard (port 8000)
```

1. **Arduino** reads voltage (A0), current (A1), and temperature (A2) at 10 Hz and sends CSV lines over serial.
2. **`new.py`** receives the serial data, runs it through the trained Random Forest model, and predicts SOC.
3. The predicted SOC is written to `soc_feed.json`, appended to an Excel file, and displayed on a live web dashboard.
4. An **ESP32** polls the JSON feed and activates a protection relay when SOC drops below 20%.

---

## 🔋 Supported Battery Profiles

| # | Battery Type         | Voltage Range | Capacity | Model File                        |
|---|----------------------|---------------|----------|-----------------------------------|
| 1 | Li-Ion (18650/Laptop)| 3.0 – 4.2 V   | 2.5 Ah   | `3V_battery_soc_model.pkl`        |
| 2 | LFP (LiFePO4)        | 2.5 – 3.65 V  | 10.0 Ah  | `3V_battery_soc_model.pkl`        |
| 3 | NiMH                 | 1.0 – 1.45 V  | 2.0 Ah   | `battery_soc_model.pkl` (generic) |
| 4 | SLA 12V              | 10.5 – 13.8 V | 7.0 Ah   | `13_battery_soc_model.pkl`        |
| 5 | SLA 24V              | 21.0 – 27.6 V | 7.0 Ah   | `24_battery_soc_model.pkl`        |

---

## ⚙️ Prerequisites

### Software
- Python 3.8+
- Arduino IDE

### Python Dependencies

```bash
pip install pyserial joblib scikit-learn openpyxl pandas numpy
```

### Arduino Libraries
- No external libraries required (uses built-in `Serial`)

---

## 🔌 Hardware & Wiring

| Sensor              | Arduino Pin | Notes                                     |
|---------------------|-------------|-------------------------------------------|
| Voltage Divider     | A0          | R1=30kΩ, R2=10kΩ → scale factor = 4.0    |
| ACS712 Current      | A1          | 5A version, sensitivity = 185 mV/A        |
| NTC Thermistor      | A2          | 10kΩ @ 25°C, Beta = 3950, series R = 10kΩ |
| GND                 | GND         | Common ground                             |
| 5V                  | 5V          | Arduino power rail                        |

> **Note:** Calibration constants (voltage divider ratio, ACS712 sensitivity, thermistor Beta) can be adjusted at the top of `battery_soc_sensor.ino` to match your specific components.

---

## 🚀 Usage

### Step 1 — Upload Arduino Firmware

1. Open `battery_soc_sensor.ino` in the Arduino IDE.
2. Select your board (`Tools > Board > Arduino Uno`) and the correct COM port.
3. Upload the sketch.
4. The Arduino will send `READY` on startup, then stream CSV lines at 10 Hz:
   ```
   VOLTAGE,CURRENT,TEMP,TIME_SECONDS
   27.195,-1.812,25.30,0.500
   ```

### Step 2 — Train the Model

Edit the paths in `BATTERY.py` to point to your training CSV and desired output directory:

```python
TRAINING_FILE = Path("D:/SOC_ML_Project/data/train/24V_LFP_Discharge_Training.csv")
MODEL_FILE    = Path("D:/SOC_ML_Project/modal/24_battery_soc_model.pkl")
FEATURES_FILE = Path("D:/SOC_ML_Project/modal/24_feature_columns.pkl")
```

Then run:

```bash
python BATTERY.py
```

The script will preprocess the data, train a `RandomForestRegressor`, print evaluation metrics (MAE, RMSE, MAPE, Accuracy), and save the model `.pkl` files.

### Step 3 — Run the Live Prediction System

Edit the paths at the top of `new.py`, then run:

```bash
python new.py
```

On startup it will:
- Pre-load all available battery models
- Start an HTTP server on port 8000
- Prompt you to select a battery type and mode

**Modes:**

| Mode   | Description                                              |
|--------|----------------------------------------------------------|
| AUTO   | Reads live data from Arduino, predicts SOC continuously  |
| MANUAL | Manually enter a SOC value to test the ESP32 relay       |
| CHANGE | Switch battery type / reload a different model           |

### Step 4 — View the Dashboard

Open a browser and navigate to:

```
http://localhost:8000/view_csv.html
```

The dashboard auto-refreshes every 3 seconds and shows current SOC, voltage, temperature, relay status, and a scrollable history table.

---

## 📊 Training Dataset

**File:** `24V_LFP_Discharge_Training.csv`

| Column        | Description                          |
|---------------|--------------------------------------|
| `Voltage`     | Battery terminal voltage (V)         |
| `Current`     | Discharge current (A, negative = discharge) |
| `Battery Temp`| Cell temperature (°C)                |
| `Time`        | Elapsed time (s)                     |
| `SOC`         | State of Charge (%, target variable) |

Additional columns (`Ah`, `Wh`, `Power`, `Chamber Temp`, `S.No`) are present in the raw file but are not used as model features.

---

## 🤖 ML Model Details

| Parameter           | Value                 |
|---------------------|-----------------------|
| Algorithm           | Random Forest Regressor |
| `n_estimators`      | 200                   |
| `max_depth`         | 20                    |
| `min_samples_split` | 4                     |
| `max_features`      | 0.5                   |
| `bootstrap`         | False                 |
| `criterion`         | squared_error         |
| Features            | Voltage, Current, Battery Temp, Time |
| Target              | SOC (0–100 %)         |

---

## 📁 Output Files

| File                         | Description                                       |
|------------------------------|---------------------------------------------------|
| `predicted_output.xlsx`      | Timestamped Excel log of all predictions          |
| `predicted_output.csv`       | Auto-exported CSV (refreshed every 4 s)           |
| `soc_feed.json`              | Live JSON feed polled by the ESP32                |
| `view_csv.html`              | Auto-generated web dashboard                      |
| `logs/debug.log`             | Detailed debug log                                |
| `modal/*.pkl`                | Trained model and feature column files            |

---

## 📡 ESP32 Integration

The ESP32 should periodically GET:

```
http://<PC_IP>:8000/soc_feed.json
```

Example response:

```json
{
  "soc": 75.34,
  "mode": "auto",
  "battery": "SLA 24V (Sealed Lead Acid)",
  "model_used": "24_battery_soc_model.pkl",
  "voltage": 26.541,
  "current": -1.812,
  "temp": 25.3,
  "ts": "2026-04-22T10:30:00.123456",
  "relay_on": false
}
```

When `relay_on` is `true` (SOC < 20%), the ESP32 should activate the protection relay to cut off the load.

---

## 🛠️ Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `SerialException: could not open port` | Arduino IDE Serial Monitor is open | Close the Serial Monitor in Arduino IDE |
| `FileNotFoundError: battery_soc_model.pkl` | Model not trained yet | Run `BATTERY.py` first |
| `ModuleNotFoundError: serial` | pyserial not installed | `pip install pyserial` |
| `OSError: [Errno 98] Address already in use` | Port 8000 is occupied | Change `_http_port` in `new.py` |
| `ValueError: could not convert` | Arduino sending non-numeric data | Check the `Serial.print()` format in the `.ino` file |
| No Arduino auto-detected | Wrong driver | Install the CH340/FTDI USB-Serial driver |

The system includes a built-in `SelfDebugger` that prints fix tips for common errors and writes full tracebacks to `logs/debug.log`.

---

## 👥 Authors

**Hari** & **Kankeshraj A**
Final Year B.E. — Electrical and Electronics Engineering (VIII Semester)

---

## 📄 License

This project was developed as an academic capstone. All rights reserved by the authors.
