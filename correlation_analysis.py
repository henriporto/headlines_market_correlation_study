import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import numpy as np
from scipy.stats import pearsonr

# Database and CSV file paths
DB_PATH = "headlines.db"
VIX_CSV_PATH = "VIX.csv"
BATCH_SIZE = 50000  # Process data in batches to manage memory

def fetch_headline_scores(batch_size=BATCH_SIZE):
    """Fetch headlines and their GPT output scores from the database in batches."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM headlines")
        total_rows = cursor.fetchone()[0]
        batches = total_rows // batch_size + (1 if total_rows % batch_size > 0 else 0)
        
        for batch in range(batches):
            query = f"SELECT ydm, output FROM headlines LIMIT {batch_size} OFFSET {batch * batch_size}"
            cursor.execute(query)
            data = cursor.fetchall()
            yield data

def adjust_and_aggregate_scores():
    """Adjust scores based on criteria and aggregate by day using batch processing."""
    daily_scores = {}
    for data_batch in fetch_headline_scores():
        for date, output in data_batch:
            try:
                score = int(output)
                adjusted_score = score - 50  # Adjusting score
            except ValueError:
                # If output is not an integer, ignore this record or log it as an error
                continue

            if date in daily_scores:
                daily_scores[date] += adjusted_score
            else:
                daily_scores[date] = adjusted_score
    return daily_scores

def read_vix_data():
    """Read VIX index data from CSV."""
    vix_data = pd.read_csv(VIX_CSV_PATH)
    vix_data['Date'] = pd.to_datetime(vix_data['Date']).dt.date
    return vix_data

def correlate_data(daily_scores, vix_data):
    """Correlate daily scores with VIX index data, ensuring only days with both scores and VIX data are included."""
    scores_df = pd.DataFrame(list(daily_scores.items()), columns=['Date', 'Score'])
    scores_df['Date'] = pd.to_datetime(scores_df['Date']).dt.date
    
    # Merging on 'Date' to ensure only days with both scores and VIX data are included
    merged_data = pd.merge(vix_data, scores_df, on='Date', how='inner')
    return merged_data

def generate_plots_and_reports(correlated_data):
    """Generate scatter plot for daily scores vs. VIX Close data, including the correlation line, statistics, and hypothesis testing results."""
    plt.figure(figsize=(10, 6))
    
    # Generating a scatter plot
    plt.scatter(correlated_data['Score'], correlated_data['Close'], color='blue', label='Data Points')
    plt.xlabel('Daily Score')
    plt.ylabel('VIX Close')
    
    # Calculating the line of best fit
    m, c = np.polyfit(correlated_data['Score'], correlated_data['Close'], 1)
    
    # Plotting the line of best fit
    plt.plot(correlated_data['Score'], m*correlated_data['Score'] + c, 'r-', label=f'Fit Line: y={m:.2f}x+{c:.2f}')
    
    # Calculating Correlation Coefficient and p-value
    correlation_coef, p_value = pearsonr(correlated_data['Score'], correlated_data['Close'])
    
    # Calculating R^2 (Coefficient of Determination)
    r_squared = correlation_coef**2
    
    # Adding text with the correlation coefficient, p-value, and R^2 value to the plot
    stats_text = f'Correlation Coefficient: {correlation_coef:.2f}\nP-value: {p_value:.3e}\nR^2: {r_squared:.2f}'
    plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, fontsize=9, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.title('Daily Headline Scores vs. VIX Close')
    plt.legend()
    plt.tight_layout()
    plt.savefig('scores_vs_vix_close_with_line_and_stats.png')
    plt.close()
    
    # Create PDF report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Daily Headline Scores vs. VIX Close Report with Correlation Line and Statistics", ln=True, align='C')
    pdf.image('scores_vs_vix_close_with_line_and_stats.png', x=10, y=20, w=180)
    pdf.output("report_scores_vs_vix_with_line_and_stats.pdf")

def main():
    adjusted_daily_scores = adjust_and_aggregate_scores()
    vix_data = read_vix_data()
    correlated_data = correlate_data(adjusted_daily_scores, vix_data)
    generate_plots_and_reports(correlated_data)

    print("Correlation analysis and report have been generated.")

if __name__ == "__main__":
    main()