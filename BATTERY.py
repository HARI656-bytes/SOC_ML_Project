"""
=============================================================================
SCRIPT 1 - Battery SOC Prediction | TRAINING PIPELINE
=============================================================================
Model   : RandomForestRegressor (pre-optimised hyperparameters)
Target  : SOC (State of Charge)
Features: Voltage, Current, Battery Temp, Time
Outputs : battery_soc_model.pkl | feature_columns.pkl
=============================================================================

HOW TO SET YOUR PATHS  (Windows-safe, no escape-sequence warnings)
-------------------------------------------------------------------
Always wrap Windows paths in  r"..."  (raw string) OR use forward slashes:

    Path(r"D:/SOC_ML_Project/data/train/Training data 1.csv")
    Path("D:/SOC_ML_Project/modal/battery_soc_model.pkl")
    Path("Training data 1.csv")   # same folder as the script

    NOTE: forward slashes  /  work fine on Windows inside Path().
=============================================================================
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

# =============================================================================
# EDIT YOUR PATHS BELOW  (use forward slashes OR raw strings)
# =============================================================================

TRAINING_FILE = Path("D:/SOC_ML_Project/data/train/24V_LFP_Discharge_Training.csv")
MODEL_FILE    = Path("D:/SOC_ML_Project/modal/24_battery_soc_model.pkl")
FEATURES_FILE = Path("D:/SOC_ML_Project/modal/24_feature_columns.pkl")

# =============================================================================

FEATURE_COLS      = ["Voltage", "Current", "Battery Temp", "Time"]
TARGET_COL        = "SOC"
VALID_VOLTAGE_MIN = 0
VALID_TEMP_MIN    = -50
VALID_TEMP_MAX    = 100


# -----------------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------------
def load_data(filepath: Path) -> pd.DataFrame:
    """Load CSV and return a raw DataFrame. Auto-detects file encoding."""
    filepath = Path(filepath)

    if not filepath.exists():
        print(f"\n  ERROR - File not found: {filepath}")
        print(f"  Resolved path: {filepath.resolve()}")
        print("  Please check the path above and retry.")
        sys.exit(1)

    for enc in ("utf-8", "latin-1", "cp1252", "utf-8-sig"):
        try:
            df = pd.read_csv(filepath, encoding=enc, low_memory=False)
            print(f"\n  Loaded {filepath.name!r}  ->  {df.shape[0]:,} rows x {df.shape[1]} columns")
            return df
        except UnicodeDecodeError:
            continue

    print(f"\n  ERROR - Could not decode {filepath!r} with any supported encoding.")
    sys.exit(1)


# -----------------------------------------------------------------------------
# 2. PREPROCESS
# -----------------------------------------------------------------------------
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
      - Strip whitespace from column names
      - Coerce all values to numeric
      - Drop rows where SOC is missing
      - Fill missing feature values with column median
      - Remove duplicate rows
      - Remove physically invalid readings (Voltage < 0, Temp out of range)
    """
    df.columns = df.columns.str.strip()
    print("\n  Columns detected:", list(df.columns))

    required = FEATURE_COLS + [TARGET_COL]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        print(f"\n  ERROR - Missing required columns: {missing}")
        print(f"  Expected: {required}")
        sys.exit(1)

    df = df[required].copy()

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df.dropna(subset=[TARGET_COL], inplace=True)
    n = before - len(df)
    if n:
        print(f"  Dropped {n:,} rows with missing SOC.")

    for col in FEATURE_COLS:
        n_miss = df[col].isna().sum()
        if n_miss:
            med = df[col].median()
            df[col].fillna(med, inplace=True)
            print(f"  Filled {n_miss:,} NaN in {col!r} with median = {med:.4f}")

    before = len(df)
    df.drop_duplicates(inplace=True)
    n = before - len(df)
    if n:
        print(f"  Removed {n:,} duplicate rows.")

    before = len(df)
    df = df[df["Voltage"] >= VALID_VOLTAGE_MIN]
    df = df[df["Battery Temp"].between(VALID_TEMP_MIN, VALID_TEMP_MAX)]
    n = before - len(df)
    if n:
        print(f"  Removed {n:,} rows with invalid Voltage / Temperature.")

    if df.empty:
        print("\n  ERROR - Dataset is empty after preprocessing.")
        sys.exit(1)

    print(f"\n  Preprocessing done  ->  {len(df):,} clean rows retained.")
    return df.reset_index(drop=True)


# -----------------------------------------------------------------------------
# 3. TRAIN MODEL
# -----------------------------------------------------------------------------
def train_model(X: pd.DataFrame, y: pd.Series) -> RandomForestRegressor:
    """Train RandomForestRegressor with pre-optimised hyperparameters on FULL dataset."""
    print(f"\n  Training RandomForestRegressor on full dataset ...")
    print(f"  Samples  : {len(X):,}")
    print(f"  Features : {list(X.columns)}")

    model = RandomForestRegressor(
        n_estimators      = 200,
        max_depth         = 20,
        min_samples_split = 4,
        min_samples_leaf  = 1,
        max_features      = 0.5,
        bootstrap         = False,
        criterion         = "squared_error",
        random_state      = 42,
        n_jobs            = -1,
    )
    model.fit(X, y)
    print("  Training complete.")
    return model


# -----------------------------------------------------------------------------
# 4. EVALUATE MODEL
# -----------------------------------------------------------------------------
def evaluate_model(model: RandomForestRegressor,
                   X: pd.DataFrame,
                   y: pd.Series) -> dict:
    """Compute and print MAE, RMSE, MAPE and Accuracy % on the training set."""
    y_pred = model.predict(X)

    mae  = mean_absolute_error(y, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
    mask = y != 0
    mape = float(np.mean(np.abs((y[mask] - y_pred[mask]) / y[mask])) * 100)
    acc  = 100.0 - mape

    sep = "=" * 47
    print(f"\n{sep}")
    print("  TRAINING EVALUATION METRICS")
    print(sep)
    print(f"  MAE       : {mae:.4f}")
    print(f"  RMSE      : {rmse:.4f}")
    print(f"  MAPE      : {mape:.4f} %")
    print(f"  Accuracy  : {acc:.4f} %")
    print(sep)
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape, "Accuracy": acc}


# -----------------------------------------------------------------------------
# 5. SAVE MODEL
# -----------------------------------------------------------------------------
def save_model(model: RandomForestRegressor,
               feature_cols: list,
               model_path: Path = MODEL_FILE,
               features_path: Path = FEATURES_FILE) -> None:
    """Persist the trained model and feature-column order to disk."""
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    Path(features_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model,        model_path)
    joblib.dump(feature_cols, features_path)
    print(f"\n  Model saved         ->  {model_path}")
    print(f"  Feature list saved  ->  {features_path}")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    sep = "=" * 55
    print(sep)
    print("   Battery SOC Predictor -- TRAINING PIPELINE")
    print(sep)

    df    = load_data(TRAINING_FILE)
    df    = preprocess(df)
    X     = df[FEATURE_COLS]
    y     = df[TARGET_COL]
    model = train_model(X, y)
    evaluate_model(model, X, y)
    save_model(model, FEATURE_COLS)

    print("\n  Done!  Run predict_battery_soc.py to make predictions.\n")


if __name__ == "__main__":
    main()
