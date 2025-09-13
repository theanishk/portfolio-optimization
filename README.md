# Portfolio Optimization

This repository contains solutions and scripts for portfolio optimization and financial analysis, including data processing, return forecasting, and volatility estimation.

## Contents

- **data/**: Contains JSON files with index data for Nifty 50, Energy, FMCG, and Pharma sectors.
- **img/**: Contains images such as the project logo and output visualizations.
- **returns/**: Contains return estimates, forecasts, and Excel files with return data.
- **scripts/**: Python scripts for data processing, modeling, and analysis.

## Scripts Overview

- [`scripts/data_script.py`](scripts/data_script.py): Data preprocessing and cleaning utilities.
- [`scripts/market.py`](scripts/market.py): Market data handling and analysis.
- [`scripts/Monthly.py`](scripts/Monthly.py): Monthly return forecasting using machine learning models (e.g., Random Forest).
- [`scripts/volatility.py`](scripts/volatility.py): Volatility estimation and related calculations.
- [`scripts/weeklyExpectedReturns.py`](scripts/weeklyExpectedReturns.py): Weekly expected returns forecasting.
- [`scripts/test.py`](scripts/test.py): Test and validation scripts.

## How to Run

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Run scripts:**
   - For monthly return forecasting:
     ```
     python scripts/Monthly.py
     ```
   - For volatility estimation:
     ```
     python scripts/volatility.py
     ```
   - For weekly expected returns:
     ```
     python scripts/weeklyExpectedReturns.py
     ```

3. **Data files:** Ensure the required data files are present in the `data/` and `returns/` directories.

## Visualization

- Output plots and results are saved in the `img/` directory.

## License

This project is for educational purposes.

---