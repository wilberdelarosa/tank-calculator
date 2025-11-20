try:
    import numpy as np
except Exception as e:
    raise ImportError(
        "numpy is required to run this script. Install it with `pip install numpy` and try again"
    ) from e

try:
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

import csv
import os
import json

# --- misma función exacta de antes ---
D = 45.0
R = D / 2.0
L = 71.0
GAL_POR_IN3 = 1.0 / 231.0

# Multi-tank system storage
_tanks = {
    "default": {
        "D": D,
        "L": L,
        "R": R,
        "name": "Tanque Principal 45x71",
        "_training_heights": [],
        "_training_galones": [],
        "modelo": None,
        "modelo_type": None
    }
}
_current_tank_id = "default"

def galones_por_altura(h, diameter=None, length=None):
    """Calculate gallons for a horizontal cylindrical tank at given height.
    If diameter and length are not provided, uses current tank dimensions."""
    _D = diameter if diameter is not None else D
    _R = _D / 2.0
    _L = length if length is not None else L
    
    if h <= 0:
        return 0.0
    if h >= _D:
        vol_in3 = np.pi * _R**2 * _L
        return vol_in3 * GAL_POR_IN3

    y = _R - h
    theta = 2.0 * np.arccos(y / _R)
    area_seg = (_R**2 / 2.0) * (theta - np.sin(theta))
    vol_in3 = area_seg * _L
    return vol_in3 * GAL_POR_IN3

# --- entrenamiento del modelo de ML ---
# Training data: start with analytic samples

# Modelo de regresión (usamos RandomForest si está disponible, si no usamos un polinomio de numpy como fallback)
def _train_model_from_data(heights, gals, n_estimators=200):
    """Train a model from numpy arrays or lists of heights and gallons.
    Returns (model, model_type) where model has a predict method or callable behavior similar to sklearn.
    """
    _x = np.array(heights).reshape(-1, 1)
    _y = np.array(gals).flatten()
    if SKLEARN_AVAILABLE:
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=42
        )
        model.fit(_x, _y)
        model_type = "sklearn_rf"
    else:
        # fallback: interpolation
        class _InterpModel:
            def __init__(self, x_vals, y_vals):
                self.x = np.array(x_vals)
                self.y = np.array(y_vals)

            def predict(self, xq):
                arr = np.asarray(xq).reshape(-1)
                # for single float
                return np.array([np.interp(float(v), self.x, self.y) for v in arr])

        model = _InterpModel(_x.flatten(), _y)
        model_type = "interp"
    return model, model_type

def _initialize_tank_training(tank_id):
    """Initialize training data for a tank"""
    tank = _tanks[tank_id]
    _D = tank["D"]
    alturas = np.linspace(0, _D, 361).reshape(-1, 1)
    galones = np.array([galones_por_altura(h[0], diameter=_D, length=tank["L"]) for h in alturas])
    
    tank["_training_heights"] = alturas.flatten().tolist()
    tank["_training_galones"] = galones.flatten().tolist()
    
    # Train initial model
    modelo, modelo_type = _train_model_from_data(tank["_training_heights"], tank["_training_galones"])
    tank["modelo"] = modelo
    tank["modelo_type"] = modelo_type

# Initialize default tank
_initialize_tank_training("default")

# Legacy global variables for backward compatibility
alturas = np.array(_tanks["default"]["_training_heights"]).reshape(-1, 1)
galones = np.array(_tanks["default"]["_training_galones"])
_training_heights = _tanks["default"]["_training_heights"]
_training_galones = _tanks["default"]["_training_galones"]
modelo = _tanks["default"]["modelo"]
modelo_type = _tanks["default"]["modelo_type"]

# Initially train model with analytic data
# (Already done in _initialize_tank_training)

def galones_ml(h, tank_id=None):
    """
    Predicción de galones usando el modelo entrenado.
    If tank_id is provided, uses that tank's model, otherwise uses current tank.
    """
    tid = tank_id if tank_id is not None else _current_tank_id
    tank = _tanks.get(tid, _tanks["default"])
    _modelo = tank["modelo"]
    _modelo_type = tank["modelo_type"]
    _D = tank["D"]
    
    h = float(np.clip(h, 0.0, _D))  # limitar a rango válido
    pred = _modelo.predict(np.array([[h]]) if _modelo_type == "sklearn_rf" else np.array([h]))
    try:
        return float(pred[0])
    except Exception:
        return float(pred)

# Ejemplo
if __name__ == "__main__":
    print("Modelo listo. (sklearn disponible: {} )".format(SKLEARN_AVAILABLE))
    while True:
        entrada = input("Altura medida (pulgadas, q para salir): ")
        if entrada.lower().startswith("q"):
            break
        try:
            h = float(entrada)
        except ValueError:
            print("Entrada no válida. Introduce un número o 'q' para salir.")
            continue
        g = galones_ml(h)
        print(f"Altura = {h:.3f} in  →  {g:.1f} galones (modelo ML)")

# ----------------------------
# Dataset, CSV I/O and calibration helper functions
# ----------------------------
import csv
import os

# Multi-tank management functions
def create_tank(name, diameter, length, tank_id=None):
    """Create a new tank with given dimensions and initialize its training data"""
    if tank_id is None:
        tank_id = f"tank_{len(_tanks)}"
    
    _tanks[tank_id] = {
        "D": float(diameter),
        "L": float(length),
        "R": float(diameter) / 2.0,
        "name": name,
        "_training_heights": [],
        "_training_galones": [],
        "modelo": None,
        "modelo_type": None
    }
    
    _initialize_tank_training(tank_id)
    
    # Auto-save tanks config
    save_tanks_config()
    
    return tank_id

def get_tank_list():
    """Return list of all tanks with their info"""
    return [{
        "id": tid,
        "name": tank["name"],
        "diameter": tank["D"],
        "length": tank["L"],
        "points": len(tank["_training_heights"])
    } for tid, tank in _tanks.items()]

def set_current_tank(tank_id):
    """Switch to a different tank"""
    global _current_tank_id, _training_heights, _training_galones, modelo, modelo_type, D, R, L
    if tank_id not in _tanks:
        raise ValueError(f"Tank {tank_id} does not exist")
    
    _current_tank_id = tank_id
    tank = _tanks[tank_id]
    
    # Update global variables for backward compatibility
    _training_heights = tank["_training_heights"]
    _training_galones = tank["_training_galones"]
    modelo = tank["modelo"]
    modelo_type = tank["modelo_type"]
    D = tank["D"]
    R = tank["R"]
    L = tank["L"]

def get_current_tank():
    """Get current tank info"""
    return {
        "id": _current_tank_id,
        **_tanks[_current_tank_id]
    }

def delete_tank(tank_id):
    """Delete a tank (cannot delete default)"""
    if tank_id == "default":
        raise ValueError("Cannot delete default tank")
    if tank_id not in _tanks:
        raise ValueError(f"Tank {tank_id} does not exist")
    
    del _tanks[tank_id]
    
    # If we deleted current tank, switch to default
    if _current_tank_id == tank_id:
        set_current_tank("default")
    
    # Auto-save after deletion
    save_tanks_config()

def save_tanks_config(filepath="tanks_config.json"):
    """Save all tanks configuration to JSON file"""
    config = {
        "current_tank_id": _current_tank_id,
        "tanks": {}
    }
    
    for tank_id, tank_data in _tanks.items():
        config["tanks"][tank_id] = {
            "name": tank_data["name"],
            "D": tank_data["D"],
            "L": tank_data["L"],
            "R": tank_data["R"],
            "_training_heights": tank_data["_training_heights"],
            "_training_galones": tank_data["_training_galones"],
            "modelo_type": tank_data["modelo_type"]
        }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def load_tanks_config(filepath="tanks_config.json"):
    """Load tanks configuration from JSON file"""
    global _tanks, _current_tank_id, _training_heights, _training_galones, modelo, modelo_type, D, R, L
    
    if not os.path.exists(filepath):
        return False
def load_tanks_config(filepath="tanks_config.json"):
    """Load tanks configuration from JSON file"""
    global _tanks, _current_tank_id, _training_heights, _training_galones, modelo, modelo_type, D, R, L
    
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Restore tanks
        _tanks.clear()
        for tank_id, tank_data in config["tanks"].items():
            _tanks[tank_id] = {
                "name": tank_data["name"],
                "D": tank_data["D"],
                "L": tank_data["L"],
                "R": tank_data["R"],
                "_training_heights": tank_data["_training_heights"],
                "_training_galones": tank_data["_training_galones"],
                "modelo": None,
                "modelo_type": tank_data.get("modelo_type", "interp")
            }
            
            # Retrain model for each tank
            if len(tank_data["_training_heights"]) > 0:
                model, model_type = _train_model_from_data(
                    tank_data["_training_heights"],
                    tank_data["_training_galones"]
                )
                _tanks[tank_id]["modelo"] = model
                _tanks[tank_id]["modelo_type"] = model_type
        
        # Restore current tank
        current_id = config.get("current_tank_id", "default")
        if current_id in _tanks:
            set_current_tank(current_id)
        else:
            set_current_tank("default")
        
        return True
    except Exception as e:
        print(f"Error loading tanks config: {e}")
        return False

# Try to load saved tanks configuration
try:
    load_tanks_config()
except:
    pass  # If no config file exists, continue with default

def load_csv_training(filepath, tank_id=None):
    """Load training CSV with two columns (Pulgadas,Galones). Returns lists (h_list, g_list).
    Accepts decimal separator dot. Ignores header and rows that cannot be parsed.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    
    h_list = []
    g_list = []
    
    # Get tank dimensions for clamping
    _tank_id = tank_id if tank_id is not None else _current_tank_id
    tank = _tanks[_tank_id]
    max_height = tank["D"]
    
    with open(filepath, 'r', newline='', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header_skipped = False
        for row in reader:
            if not row:
                continue
            if not header_skipped:
                # assume first row is header if not numeric
                try:
                    float(row[0])
                except Exception:
                    header_skipped = True
                    continue
            try:
                h_val = float(row[0])
                g_val = float(row[1])
            except Exception:
                continue
            # clamp height to valid range
            if h_val < 0:
                h_val = 0.0
            if h_val > max_height:
                h_val = max_height
            h_list.append(h_val)
            g_list.append(g_val)
    return h_list, g_list

def append_training_points(h_vals, g_vals, tank_id=None):
    """Append given lists of heights and gallons to the internal dataset and retrain the model.
    h_vals and g_vals are iterables (scalars allowed) – will coerce to lists.
    Returns new model and metrics.
    """
    global _training_heights, _training_galones, modelo, modelo_type
    
    _tank_id = tank_id if tank_id is not None else _current_tank_id
    tank = _tanks[_tank_id]
    
    if np.isscalar(h_vals):
        h_vals = [float(h_vals)]
    if np.isscalar(g_vals):
        g_vals = [float(g_vals)]
    
    for h, g in zip(h_vals, g_vals):
        tank["_training_heights"].append(float(h))
        tank["_training_galones"].append(float(g))
    
    # Retrain model for this tank
    model, model_type = _train_model_from_data(
        tank["_training_heights"],
        tank["_training_galones"]
    )
    tank["modelo"] = model
    tank["modelo_type"] = model_type
    
    # Update globals if this is the current tank
    if _tank_id == _current_tank_id:
        _training_heights = tank["_training_heights"]
        _training_galones = tank["_training_galones"]
        modelo = model
        modelo_type = model_type
    
    # Auto-save config
    save_tanks_config()
    
    return model, model_type

def _retrain_model(n_estimators=200):
    global modelo, modelo_type
    modelo, modelo_type = _train_model_from_data(_training_heights, _training_galones, n_estimators=n_estimators)

def save_training_csv(filepath):
    """Save the current training dataset to CSV with header Pulgadas,Galones"""
    with open(filepath, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['Pulgadas', 'Galones'])
        for h, g in zip(_training_heights, _training_galones):
            writer.writerow([h, g])

def get_training_dataset():
    """Return numpy arrays (heights, gallons) for the current training dataset."""
    return np.array(_training_heights), np.array(_training_galones)

def reset_training_to_analytic(n_samples=361):
    """Reset the training dataset to only the analytic sample values (equally spaced)."""
    global _training_heights, _training_galones
    alturas = np.linspace(0, D, n_samples)
    galones_vals = np.array([galones_por_altura(h) for h in alturas])
    _training_heights = alturas.tolist()
    _training_galones = galones_vals.tolist()
    _retrain_model()


def evaluate_model_on_dataset(model_obj, heights, gallons):
    """Return MAE and RMSE of model predictions on provided dataset (iterables)."""
    x = np.array(heights)
    y = np.array(gallons)
    preds = model_obj.predict(x.reshape(-1, 1) if modelo_type == 'sklearn_rf' else x.flatten())
    preds = np.array(preds).flatten()
    if preds.shape != y.shape:
        preds = preds[:y.shape[0]]
    mae = np.mean(np.abs(preds - y))
    rmse = np.sqrt(np.mean((preds - y)**2))
    return mae, rmse

def load_and_merge_csv(filepath, tank_id=None):
    """Load CSV and merge with existing training data for specified tank"""
    global _training_heights, _training_galones, modelo, modelo_type
    
    _tank_id = tank_id if tank_id is not None else _current_tank_id
    tank = _tanks[_tank_id]
    
    h_list, g_list = load_csv_training(filepath, tank_id)
    if not h_list:
        return 0
    
    for h, g in zip(h_list, g_list):
        tank["_training_heights"].append(h)
        tank["_training_galones"].append(g)
    
    # Retrain model for this tank
    model, model_type = _train_model_from_data(
        tank["_training_heights"],
        tank["_training_galones"]
    )
    tank["modelo"] = model
    tank["modelo_type"] = model_type
    
    # Update globals if this is the current tank
    if _tank_id == _current_tank_id:
        _training_heights = tank["_training_heights"]
        _training_galones = tank["_training_galones"]
        modelo = model
        modelo_type = model_type
    
    # Auto-save config
    save_tanks_config()
    
    return len(h_list)
