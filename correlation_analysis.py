import pandas as pd
import sqlite3
from scipy.stats import pearsonr, linregress
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

DB = "headlines.db"
VIX_CSV = "VIX.csv"

def calculate_correlation_and_plot(db_path, vix_csv_path):
    """
    Calculate the Pearson correlation coefficient between WSJ headlines' impact scores
    and various VIX index metrics. Generate enhanced plots of these relationships and save them as a PDF.
    """
    # Connect to SQLite database and load WSJ headlines data
    conn = sqlite3.connect(db_path)
    query = "SELECT ydm, output FROM headlines"
    headlines_df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure 'output' is numeric
    headlines_df["output"] = pd.to_numeric(headlines_df["output"], errors="coerce")

    # Load VIX Index Data
    vix_df = pd.read_csv(vix_csv_path)
    vix_df["Date"] = pd.to_datetime(vix_df["Date"])

    # Calculate daily percentage changes for VIX metrics
    for column in ["Open", "High", "Low", "Close", "Adj Close"]:
        vix_df[f"{column.lower()}_change"] = vix_df[column].pct_change() * 100

    # Prepare Data - ensure all data frames use datetime and are aligned
    headlines_df["ydm"] = pd.to_datetime(headlines_df["ydm"])

    # Merge WSJ headlines data with VIX on date
    data_merged = pd.merge(headlines_df, vix_df, left_on="ydm", right_on="Date")

    # Drop rows with NaN values
    data_merged.dropna(subset=["output"] + [f"{col}_change" for col in ["open", "high", "low", "close", "adj_close"]], inplace=True)

    # Plotting and saving to PDF
    with PdfPages('vix_correlation_plots_enhanced.pdf') as pdf:
        for metric in ["open_change", "high_change", "low_change", "close_change", "adj_close_change"]:
            # Calculate Pearson correlation coefficient and its p-value
            correlation_coefficient, pearson_p_value = pearsonr(data_merged["output"], data_merged[metric])
            
            # Calculate linear regression for trend line and its p-value
            slope, intercept, r_value, linreg_p_value, std_err = linregress(data_merged["output"], data_merged[metric])
            
            plt.figure(figsize=(10, 6))
            plt.scatter(data_merged["output"], data_merged[metric], alpha=0.5, color='dodgerblue')
            plt.plot(data_merged["output"], intercept + slope*data_merged["output"], 'r', label=f'y={slope:.2f}x+{intercept:.2f}')
            
            # Updated title to include both Pearson correlation p-value and linear regression p-value
            plt.title(f'WSJ Impact vs. VIX {metric}\nCorrelation: {correlation_coefficient:.2f}, Pearson P-value: {pearson_p_value:.2e}, LinReg P-value: {linreg_p_value:.2e}')
            
            plt.xlabel('WSJ Impact Score')
            plt.ylabel(f'VIX {metric.capitalize()} (%)')
            plt.grid(True)
            plt.legend()
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()

def main():
    calculate_correlation_and_plot(DB, VIX_CSV)

if __name__ == "__main__":
    main()
