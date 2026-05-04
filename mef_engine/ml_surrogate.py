"""
ml_surrogate.py — Motor de Surrogate Modeling (M5-PhD).
Aprende a prever resultados do MEF para iterações ultra-rápidas.
"""
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import pickle
from pathlib import Path

class StructuralSurrogate:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(64, 64), max_iter=1000, random_state=42)
        self.scaler_x = StandardScaler()
        self.scaler_y = StandardScaler()
        self.is_trained = False

    def generate_training_data(self, n_samples: int = 50) -> pd.DataFrame:
        """Gera dados sintéticos usando o motor analítico para treino."""
        from radier_analytical import calculate_rigid_soil_pressure, AnalyticalConfig
        
        data = []
        for _ in range(n_samples):
            Lx = np.random.uniform(10, 40)
            Ly = np.random.uniform(10, 40)
            h = np.random.uniform(0.3, 1.2)
            kv = np.random.uniform(10e6, 80e6)
            q = np.random.uniform(50e3, 300e3)
            
            # Carga uniforme fictícia para o analítico
            cfg = AnalyticalConfig(Lx=Lx, Ly=Ly, loads_kN=np.array([[0,0,0]]), q_uniform_Pa=q)
            res = calculate_rigid_soil_pressure(cfg)
            
            # Recalque aproximado: w = q/kv
            w_max = (q / kv) * 1000.0
            
            data.append({
                'Lx': Lx, 'Ly': Ly, 'h': h, 'kv': kv, 'q': q,
                'w_max_mm': w_max,
                'q_max_kPa': res['q_max_rigid_kPa']
            })
            
        return pd.DataFrame(data)

    def train(self, df: pd.DataFrame):
        X = df[['Lx', 'Ly', 'h', 'kv', 'q']]
        y = df[['w_max_mm', 'q_max_kPa']]
        
        X_scaled = self.scaler_x.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y)
        
        self.model.fit(X_scaled, y_scaled)
        self.is_trained = True

    def predict(self, Lx: float, Ly: float, h: float, kv: float, q: float) -> Dict[str, float]:
        if not self.is_trained:
            return {"error": "Modelo não treinado"}
            
        X = np.array([[Lx, Ly, h, kv, q]])
        X_scaled = self.scaler_x.transform(X)
        y_scaled = self.model.predict(X_scaled)
        y_pred = self.scaler_y.inverse_transform(y_scaled)
        
        return {
            "w_max_mm_pred": float(y_pred[0][0]),
            "q_max_kPa_pred": float(y_pred[0][1]),
            "method": "ML_Surrogate_v1"
        }

    def save_model(self, path: str = "surrogate_model.pkl"):
        with open(path, 'wb') as f:
            pickle.dump({'model': self.model, 'sx': self.scaler_x, 'sy': self.scaler_y}, f)

    def load_model(self, path: str = "surrogate_model.pkl"):
        if Path(path).exists():
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler_x = data['sx']
                self.scaler_y = data['sy']
                self.is_trained = True

if __name__ == "__main__":
    surrogate = StructuralSurrogate()
    print("Gerando dados e treinando modelo PhD...")
    df = surrogate.generate_training_data(100)
    surrogate.train(df)
    
    test_res = surrogate.predict(24.0, 24.0, 0.70, 40e6, 140e3)
    print(f"Previsão ML: {test_res}")
