# ⚡ AI-Driven Real-Time Battery SOC Estimation with Intelligent Power Control

A machine-learning-based battery monitoring and intelligent power-control system that estimates **State of Charge (SOC) in real time** using live sensor data from an Arduino, a trained **Random Forest Regressor**, and an **ESP32-based relay control system**.

The proposed system combines **multi-parameter SOC estimation, real-time monitoring, data logging, web visualization, and intelligent load protection** into a single architecture. Unlike conventional voltage-threshold protection, the system considers **voltage, current, battery temperature, and elapsed discharge time** to estimate the battery's actual SOC before making a load-control decision.

---

## 📌 Project Overview

Accurate State of Charge estimation is an important requirement in **Battery Management Systems (BMS)** because battery voltage alone does not always represent the actual remaining capacity. During high-current conditions, for example, terminal voltage can temporarily decrease because of **load-induced voltage sag**, potentially causing conventional voltage-threshold systems to disconnect the load prematurely.

This project addresses this limitation using a **data-driven Random Forest Regression model** trained on experimentally recorded battery-discharge data.

The system:

* Acquires battery voltage, current, and temperature using an Arduino.
* Uses elapsed discharge time as an additional model feature.
* Predicts SOC continuously using a trained Random Forest model.
* Provides a real-time web dashboard.
* Logs measurements and predictions to Excel/CSV.
* Publishes the latest prediction through a JSON feed.
* Allows an ESP32 to make an intelligent relay-control decision.
* Activates load protection when the estimated SOC falls below **20%**.
* Supports different battery profiles through independently trained models.

---

## 🎯 Research Objective

The primary objective is to develop a **real-time, machine-learning-based battery SOC estimation and intelligent power-control system** capable of operating under dynamic discharge conditions.

The system is designed to demonstrate that combining multiple battery parameters can provide a more informative SOC estimate than relying solely on terminal-voltage thresholds.

### Main objectives

1. Develop a machine-learning model for real-time SOC estimation.
2. Use experimentally measured voltage, current, temperature, and time as prediction features.
3. Evaluate the model using standard regression metrics.
4. Integrate the ML prediction system with an ESP32.
5. Implement intelligent load protection based on estimated SOC.
6. Provide real-time visualization and data logging.
7. Reduce premature load disconnection caused by temporary voltage fluctuations.

---

# 🏗️ System Architecture

```text
                     ┌─────────────────────┐
                     │     Battery Pack    │
                     └──────────┬──────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
       Voltage Sensor      ACS712 Current     Temperature
          / Divider           Sensor             Sensor
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │       Arduino       │
                     │  Sensor Acquisition │
                     └──────────┬──────────┘
                                │ USB Serial
                                ▼
                     ┌─────────────────────┐
                     │      Python         │
                     │  Real-Time System   │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Random Forest Model │
                     │    SOC Prediction   │
                     └──────────┬──────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
               ▼                ▼                ▼
         Excel / CSV       Web Dashboard     JSON Feed
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │    ESP32    │
                                           └──────┬──────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │    Relay    │
                                           └──────┬──────┘
                                                  │
                                                  ▼
                                               Load
```

---

# 🧠 How the System Works

The complete system consists of four major stages:

### 1. Sensor Data Acquisition

The Arduino continuously measures:

* Battery voltage
* Battery current
* Battery temperature
* Elapsed discharge time

The measurements are transmitted through USB serial communication to the Python application.

Example:

```text
VOLTAGE,CURRENT,TEMP,TIME_SECONDS
27.195,-1.812,25.30,0.500
```

---

### 2. Machine Learning SOC Estimation

The Python application receives the sensor data and passes the following four features to the trained Random Forest model:

```text
Voltage
Current
Battery Temperature
Time
```

The model generates a continuous SOC prediction between approximately:

```text
0% ─────────────────────────────── 100%
```

---

### 3. Real-Time Data Processing

The predicted SOC and corresponding sensor measurements are:

* Displayed on the web dashboard.
* Stored in Excel.
* Exported to CSV.
* Written to `soc_feed.json`.
* Used by the ESP32 for relay-control decisions.

---

### 4. Intelligent Power Control

The ESP32 periodically reads the JSON feed from the Python server.

```text
SOC ≥ 20%
      │
      ▼
  Relay ON
  Load Enabled

SOC < 20%
      │
      ▼
 Relay OFF
 Load Protected
```

The 20% threshold is implemented as a **protective operating limit**, rather than as the SOC estimation method itself.

---

# 🔋 Supported Battery Profiles

| # | Battery Type          | Voltage Range | Capacity | Model                      |
| - | --------------------- | ------------: | -------: | -------------------------- |
| 1 | Li-Ion 18650 / Laptop |     3.0–4.2 V |   2.5 Ah | `3V_battery_soc_model.pkl` |
| 2 | LFP / LiFePO4         |    2.5–3.65 V |    10 Ah | `3V_battery_soc_model.pkl` |
| 3 | NiMH                  |    1.0–1.45 V |     2 Ah | `battery_soc_model.pkl`    |
| 4 | SLA 12 V              |   10.5–13.8 V |     7 Ah | `13_battery_soc_model.pkl` |
| 5 | SLA 24 V              |   21.0–27.6 V |     7 Ah | `24_battery_soc_model.pkl` |

> **Important:** A model should only be used with the battery chemistry, voltage configuration, and operating conditions represented by its training data. A model trained on one battery profile should not automatically be assumed to generalize to another chemistry.

---

# 📊 Dataset and Experimental Discharge Conditions

## Training Dataset

**Dataset:** `24V_LFP_Discharge_Training.csv`

The dataset contains experimentally recorded battery-discharge measurements.

| Column         | Description                                              |
| -------------- | -------------------------------------------------------- |
| `Voltage`      | Battery terminal voltage (V)                             |
| `Current`      | Battery current (A); negative values represent discharge |
| `Battery Temp` | Battery temperature (°C)                                 |
| `Time`         | Elapsed discharge time (s)                               |
| `SOC`          | State of Charge (%)                                      |

Additional recorded parameters include:

```text
Ah
Wh
Power
Chamber Temp
S.No
```

These additional parameters are retained in the raw dataset but are not used as primary model input features in the current implementation.

---

## ⚡ Clarification on C-Rates

The training dataset should be interpreted as a **continuous dynamic discharge dataset**, rather than as three independent static datasets corresponding exclusively to 0.5C, 1C, and 2C operating points.

The battery discharge experiment records continuously varying electrical measurements under the applied discharge conditions. Consequently, the machine-learning model learns relationships between SOC and the measured operating parameters across the recorded discharge trajectory.

This approach is useful for demonstrating model behavior under **dynamic operating conditions**, where voltage and current can vary during the discharge process.

> The exact C-rate coverage and experimental protocol should be reported according to the actual laboratory test procedure and dataset. The model should not be described as being trained across 0.5C, 1C, and 2C conditions unless those conditions are explicitly represented in the experimental dataset.

---

# 🤖 Machine Learning Model

The project uses a:

**Random Forest Regressor**

### Model Configuration

| Parameter           |                                Value |
| ------------------- | -----------------------------------: |
| Algorithm           |              Random Forest Regressor |
| `n_estimators`      |                                  200 |
| `max_depth`         |                                   20 |
| `min_samples_split` |                                    4 |
| `max_features`      |                                  0.5 |
| `bootstrap`         |                                False |
| `criterion`         |                      `squared_error` |
| Input Features      | Voltage, Current, Battery Temp, Time |
| Target              |                              SOC (%) |

---

# ⚖️ Feature Weighting and Importance

No manually assigned weights or prior weighting coefficients are applied to the input variables.

Instead, the Random Forest model uses a **data-driven learning process** to determine how useful each feature is for reducing prediction error during tree construction.

The model uses the:

```text
criterion = squared_error
```

criterion to evaluate candidate splits.

The resulting feature importance values from the trained model were:

| Feature             | Importance |
| ------------------- | ---------: |
| Voltage             |      54.2% |
| Current             |      22.8% |
| Time                |      13.5% |
| Battery Temperature |       9.5% |

```text
Voltage              ███████████████████████████ 54.2%
Current              ███████████                 22.8%
Time                 ███████                     13.5%
Battery Temperature  █████                       9.5%
```

These values represent **model-derived feature importance**, not manually assigned feature weights.

### Interpretation

Voltage has the largest contribution to the trained model because it provides strong information about the battery's discharge state. Current captures the effect of the instantaneous operating condition, while elapsed time provides information about the progression of the discharge process. Temperature contributes additional information regarding the battery's operating condition.

The importance values are specific to the trained dataset and model. They should therefore not be interpreted as universal physical constants or as fixed weighting coefficients applicable to every battery chemistry or operating condition.

---

# 🧪 Model Evaluation

The training pipeline evaluates the Random Forest model using standard regression metrics.

### Evaluation metrics

* **MAE** — Mean Absolute Error
* **RMSE** — Root Mean Square Error
* **MAPE** — Mean Absolute Percentage Error
* **Accuracy / tolerance-based accuracy**, where implemented

Example output:

```text
Mean Absolute Error : XX.XXXX
RMSE                : XX.XXXX
MAPE                : XX.XXXX %
Accuracy            : XX.XX %
```

> Actual values should be generated from the current training run rather than hard-coded into the documentation.

---

# 🔌 Hardware Configuration

| Component             | Arduino Pin | Configuration             |
| --------------------- | ----------- | ------------------------- |
| Voltage Divider       | A0          | R1 = 30 kΩ, R2 = 10 kΩ    |
| ACS712 Current Sensor | A1          | 5 A version, 185 mV/A     |
| NTC Thermistor        | A2          | 10 kΩ @ 25°C, Beta = 3950 |
| Ground                | GND         | Common ground             |
| Supply                | 5V          | Arduino power rail        |

### Voltage Divider

For:

```text
R1 = 30 kΩ
R2 = 10 kΩ
```

the voltage-divider relationship is:

```text
Vout = Vin × R2 / (R1 + R2)
```

Therefore:

```text
Vout = Vin × 10 / 40
Vout = Vin / 4
```

The corresponding theoretical input scaling factor is:

```text
Vin = Vout × 4
```

The actual calibration factor should be verified experimentally before use.

---

# 🚀 Installation

## Software Requirements

* Python 3.8 or later
* Arduino IDE
* Arduino-compatible board
* ESP32 development environment

## Python Dependencies

```bash
pip install pyserial joblib scikit-learn openpyxl pandas numpy
```

---

# 📁 Project Structure

```text
SOC_ML_Project/
│
├── BATTERY.py
├── new.py
├── battery_soc_sensor.ino
│
├── 24V_LFP_Discharge_Training.csv
│
├── Picture2.jpg
├── Picture7.png
│
├── modal/
│   ├── 24_battery_soc_model.pkl
│   └── 24_feature_columns.pkl
│
├── logs/
│   └── debug.log
│
├── predicted_output.xlsx
├── predicted_output.csv
├── soc_feed.json
└── view_csv.html
```

---

# ⚙️ Installation and Usage

## Step 1 — Upload Arduino Firmware

Open:

```text
battery_soc_sensor.ino
```

in Arduino IDE.

Select:

```text
Tools → Board → Arduino Uno
```

Select the correct COM port and upload the firmware.

After startup, the Arduino sends:

```text
READY
```

followed by continuous sensor data.

---

## Step 2 — Train the Random Forest Model

Configure the dataset and output paths in `BATTERY.py`.

Example:

```python
TRAINING_FILE = Path(
    "D:/SOC_ML_Project/data/train/24V_LFP_Discharge_Training.csv"
)

MODEL_FILE = Path(
    "D:/SOC_ML_Project/modal/24_battery_soc_model.pkl"
)

FEATURES_FILE = Path(
    "D:/SOC_ML_Project/modal/24_feature_columns.pkl"
)
```

Run:

```bash
python BATTERY.py
```

The training pipeline:

1. Loads the dataset.
2. Selects the required features.
3. Performs preprocessing.
4. Trains the Random Forest model.
5. Evaluates model performance.
6. Calculates feature importance.
7. Saves the trained model.
8. Saves the feature-column configuration.

---

# 🖥️ Step 3 — Run the Real-Time Prediction System

Configure the required paths and serial settings in:

```text
new.py
```

Then execute:

```bash
python new.py
```

The application:

* Loads available battery models.
* Detects/opens the Arduino serial interface.
* Starts the HTTP server.
* Processes incoming sensor data.
* Predicts SOC continuously.
* Updates the JSON feed.
* Logs measurements.
* Updates the dashboard.

---

# 🎛️ Operating Modes

| Mode     | Function                                         |
| -------- | ------------------------------------------------ |
| `AUTO`   | Reads Arduino data and continuously predicts SOC |
| `MANUAL` | Allows manual SOC entry for relay testing        |
| `CHANGE` | Changes battery profile/model                    |

---

# 🌐 Real-Time Dashboard

After starting the Python application, open:

```text
http://localhost:8000/view_csv.html
```

The dashboard provides:

* Current SOC
* Battery voltage
* Current
* Temperature
* Relay state
* Prediction history
* Timestamp
* Logged measurement information

The dashboard automatically refreshes periodically.

---

# 📡 ESP32 Integration

The ESP32 communicates with the Python server using the JSON feed:

```text
http://<PC_IP>:8000/soc_feed.json
```

Example:

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

---

# 🔒 Intelligent 20% SOC Cutoff

The system implements a **20% SOC threshold** for protective load control.

```text
                 ML SOC Prediction
                        │
              ┌─────────┴─────────┐
              │                   │
           SOC ≥ 20%           SOC < 20%
              │                   │
              ▼                   ▼
          Load Enabled        Load Disabled
          Relay ON            Relay OFF
```

## Why use estimated SOC instead of voltage alone?

A conventional voltage-based cutoff may react to temporary voltage drops caused by increased load.

For example:

```text
High Load
   ↓
Current increases
   ↓
Temporary voltage sag
   ↓
Voltage crosses threshold
   ↓
Conventional system may disconnect load
```

The proposed system instead evaluates multiple parameters:

```text
Voltage
   +
Current
   +
Temperature
   +
Discharge Time
   ↓
Random Forest
   ↓
Estimated SOC
   ↓
Protection Decision
```

This enables the cutoff decision to be based on the **estimated battery state**, rather than on a single instantaneous voltage measurement.

> The system is designed to reduce premature cutoff caused by transient voltage sag; this claim should be supported by comparative experimental results if presented as a quantitative research conclusion.

---

# 🆚 Conventional vs Proposed Approach

| Parameter                    | Conventional Voltage Cutoff | Proposed ML-Based Control              |
| ---------------------------- | --------------------------- | -------------------------------------- |
| Primary input                | Battery voltage             | Voltage + Current + Temperature + Time |
| SOC estimation               | Indirect / threshold-based  | Machine-learning regression            |
| Load-induced voltage sag     | Can cause false cutoff      | Considered alongside other variables   |
| Dynamic operating conditions | Limited                     | Designed for dynamic measurements      |
| Continuous SOC prediction    | Usually unavailable         | Yes                                    |
| Data logging                 | Optional                    | Integrated                             |
| Web monitoring               | Usually unavailable         | Integrated                             |
| Remote/control interface     | Limited                     | ESP32 JSON interface                   |
| Intelligent relay control    | Threshold based             | SOC-estimation based                   |

---

# 📈 Research Significance

The major contribution of the project is the integration of:

```text
Experimental Battery Data
          +
Machine Learning
          +
Real-Time Embedded Acquisition
          +
Web-Based Monitoring
          +
ESP32 Closed-Loop Power Control
```

The system therefore extends SOC estimation beyond an offline machine-learning experiment and demonstrates its integration into a **real-time battery monitoring and protection architecture**.

---

# 📊 Output Files

| File                     | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `predicted_output.xlsx`  | Timestamped prediction and sensor log             |
| `predicted_output.csv`   | Continuously exported prediction data             |
| `soc_feed.json`          | Real-time data feed for ESP32                     |
| `view_csv.html`          | Web-based monitoring dashboard                    |
| `logs/debug.log`         | Detailed application/debug log                    |
| `modal/*.pkl`            | Trained ML model and feature configuration        |
| `feature_importance.png` | Visualization of model-derived feature importance |

---

# 🛠️ Troubleshooting

| Error                                  | Possible Cause                    | Solution                                                  |
| -------------------------------------- | --------------------------------- | --------------------------------------------------------- |
| `SerialException: could not open port` | Serial Monitor is using the port  | Close Arduino Serial Monitor                              |
| `FileNotFoundError`                    | Model does not exist              | Run `BATTERY.py` first                                    |
| `ModuleNotFoundError: serial`          | pyserial missing                  | `pip install pyserial`                                    |
| `Address already in use`               | Port 8000 occupied                | Change HTTP port or stop the existing process             |
| `ValueError: could not convert`        | Invalid Arduino output            | Verify `Serial.print()` formatting                        |
| Arduino not detected                   | Driver/USB issue                  | Check USB connection and CH340/FTDI driver                |
| ESP32 cannot access JSON               | PC firewall/network configuration | Allow port 8000 and verify PC IP                          |
| Incorrect SOC                          | Calibration/training mismatch     | Verify sensor calibration and training-data compatibility |

The application includes a `SelfDebugger` component that provides troubleshooting information and records detailed errors in:

```text
logs/debug.log
```

---

# 🔬 Limitations and Future Work

## Current Limitations

* Model performance depends strongly on the quality and operating range of the training dataset.
* A model trained for one battery chemistry should not automatically be generalized to another chemistry.
* Sensor calibration directly affects SOC prediction accuracy.
* The 20% cutoff is an application-level protection threshold and should be validated against the battery manufacturer's recommended operating limits.
* Real-time prediction performance depends on the quality and representativeness of the experimental dataset.

## Future Improvements

Potential future developments include:

* Training with multiple C-rates.
* Testing under dynamic load profiles.
* Cross-validation across multiple discharge cycles.
* Testing on independent battery cells/packs.
* Comparison with Coulomb Counting and Extended Kalman Filter methods.
* Hyperparameter optimization.
* Online/continual learning.
* Cloud-based battery monitoring.
* Mobile monitoring application.
* Integration with a complete BMS.
* State of Health (SOH) estimation.
* Remaining Useful Life (RUL) prediction.

---

# 👥 Authors

**Hari & Kankeshraj A**

Final Year B.E. — Electrical and Electronics Engineering
VIII Semester

---

# 📄 License

This project was developed as an academic capstone project.

**All rights reserved by the authors.**
