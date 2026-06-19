# SIDM — Smart Intrusion Detection & Prevention Model

A hybrid machine learning system for real-time detection and 
prevention of cyber attacks on Ethereum-connected networks.

## Overview

SIDM combines three machine learning models in a weighted ensemble 
to classify network transactions as Normal or Malicious in real time. 
The system integrates live Ethereum Mainnet data via Infura and 
presents results through an interactive Streamlit dashboard.

## Architecture

| Component | Technology |
|-----------|-----------|
| Model 1 | Random Forest (150 estimators) |
| Model 2 | XGBoost |
| Model 3 | LSTM (Deep Learning) |
| Ensemble | Average probability fusion |
| Blockchain | Ethereum Mainnet via Infura Web3 |
| Frontend | Streamlit |
| Backend | Python, Scikit-learn, TensorFlow, Joblib |

## How to Run

### 1. Clone the repository
git clone https://github.com/markuskay/SIDM-Smart-Intrusion-Detection.git
cd SIDM-Smart-Intrusion-Detection

### 2. Install dependencies
pip install -r requirements.txt

### 3. Train the models
Open and run the full notebook:
notebooks/Adaji_Model.ipynb
This will save rf_model.pkl, xgb_model.pkl, and lstm_model.h5 
to your local models/ folder.

### 4. Update model paths in the app
Open app/aymodel.py and update the file paths in the 
load_models() function to match your local directory.

### 5. Launch the dashboard
streamlit run app/aymodel.py

### 6. Login credentials
Username: admin
Password: sidm123

## Key Features

- Live Ethereum Integration: pulls real-time wallet balance, 
  transaction count, and gas prices via Infura API
- Hybrid Ensemble Detection: Random Forest + XGBoost + LSTM 
  averaging for high-confidence threat classification
- Real-Time Prediction: classifies transactions as Normal 
  or Malicious with confidence percentage
- Prevention Controls: block IP, rate limit, deploy firewall 
  rules against detected threats
- Audit Logs: exportable CSV logs of all detection events

## Model Performance

| Model | Role |
|-------|------|
| Random Forest | Fast tabular classification, feature importance |
| XGBoost | High accuracy gradient boosting |
| LSTM | Sequential temporal pattern detection |
| Ensemble | Combined average probability output |

## Technical Decisions

- Three-model ensemble chosen to cover each models individual 
  blind spots across tabular and sequential data patterns
- Streamlit selected for rapid deployment over React frontend
- Infura primary with public RPC fallback to ensure uptime
- Stratified train-test split to handle class imbalance

## Known Limitations

- Scaler is fit at inference time rather than saved from training
- Model files must be generated locally before running the app
- Infura free tier may throttle under high request volume

## Future Improvements

- Replace LSTM with Transformer architecture
- Save and load fitted scaler alongside models
- Deploy with FastAPI backend and React frontend
- Add concept drift detection for automatic retraining
- Integrate Graph Neural Network for
