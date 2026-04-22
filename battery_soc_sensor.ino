// =============================================================================
// battery_soc_sensor.ino
// Battery SOC Sensor — Arduino Uno
// =============================================================================
//
// WIRING:
//   Voltage Divider  → A0   (scale battery voltage to 0-5V range)
//   ACS712 Current   → A1   (current sensor output)
//   NTC Thermistor   → A2   (temperature sensor)
//   GND              → GND
//   5V               → 5V
//
// SERIAL OUTPUT FORMAT (one line per reading):
//   VOLTAGE,CURRENT,TEMP,TIME
//   Example: 4.145,-1.812,21.78,0.500
//
// =============================================================================

// ── PIN DEFINITIONS ──────────────────────────────────────────────────────────
const int PIN_VOLTAGE = A0;
const int PIN_CURRENT = A1;
const int PIN_TEMP    = A2;

// ── CALIBRATION CONSTANTS ─────────────────────────────────────────────────────
// Voltage divider: R1=30kΩ, R2=10kΩ  → scale factor = (R1+R2)/R2
const float VOLTAGE_DIVIDER_RATIO = 4.0;    // adjust to your resistor values
const float ADC_REF               = 5.0;    // Arduino Uno reference voltage
const float ADC_RESOLUTION        = 1023.0;

// ACS712-5A: sensitivity = 185 mV/A, zero = 2.5V (Vcc/2)
const float ACS712_SENSITIVITY    = 0.185;  // V per Amp
const float ACS712_ZERO_VOLTAGE   = 2.5;    // V at zero current

// NTC Thermistor: Steinhart-Hart simplified (Beta model)
const float THERMISTOR_NOMINAL    = 10000.0;  // 10kΩ at 25°C
const float SERIES_RESISTOR       = 10000.0;  // 10kΩ series resistor
const float NOMINAL_TEMP          = 25.0;     // nominal temp (°C)
const float BETA_COEFFICIENT      = 3950.0;   // Beta value from datasheet

// ── TIMING ───────────────────────────────────────────────────────────────────
const unsigned long SAMPLE_INTERVAL_MS = 100;  // 100 ms = 10 Hz sample rate

unsigned long lastSampleTime  = 0;
unsigned long startTime       = 0;


// =============================================================================
void setup() {
  Serial.begin(9600);
  startTime = millis();

  // Handshake — Python waits for this before reading data
  Serial.println("READY");
}


// =============================================================================
void loop() {
  unsigned long now = millis();

  if (now - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = now;

    float voltage = readVoltage();
    float current = readCurrent();
    float temp    = readTemperature();
    float timeSec = (now - startTime) / 1000.0;

    // Send CSV line: VOLTAGE,CURRENT,TEMP,TIME_SECONDS
    Serial.print(voltage, 4);
    Serial.print(",");
    Serial.print(current, 4);
    Serial.print(",");
    Serial.print(temp, 4);
    Serial.print(",");
    Serial.println(timeSec, 4);
  }
}


// =============================================================================
// SENSOR READING FUNCTIONS
// =============================================================================

float readVoltage() {
  int   raw = analogRead(PIN_VOLTAGE);
  float v   = (raw / ADC_RESOLUTION) * ADC_REF;
  return v * VOLTAGE_DIVIDER_RATIO;   // scale back to actual battery voltage
}


float readCurrent() {
  // Average 10 readings to reduce noise
  long  sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(PIN_CURRENT);
    delayMicroseconds(100);
  }
  float raw_v  = ((sum / 10.0) / ADC_RESOLUTION) * ADC_REF;
  float current = (raw_v - ACS712_ZERO_VOLTAGE) / ACS712_SENSITIVITY;

  // Negative = discharging (convention used in training data)
  return current;
}


float readTemperature() {
  int   raw        = analogRead(PIN_TEMP);
  float resistance = SERIES_RESISTOR * ((ADC_RESOLUTION / raw) - 1.0);

  // Steinhart-Hart Beta model
  float steinhart  = resistance / THERMISTOR_NOMINAL;
  steinhart        = log(steinhart);
  steinhart       /= BETA_COEFFICIENT;
  steinhart       += 1.0 / (NOMINAL_TEMP + 273.15);
  steinhart        = 1.0 / steinhart;
  float tempC      = steinhart - 273.15;

  return tempC;
}
