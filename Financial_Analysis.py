# 🚀 Personalized Financial Dashboard
import smtplib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from email.mime.text import MIMEText


# Function 1 :- Project Setup & Dataset Acquisition
# Function 2: Load, Clean, Analyze Financial Data
# Function 4:- Exploratory Data Analysis (EDA)
# Function 5:- Statistical Summaries and Trends
# Step 1: Load CSV
df = pd.read_csv(r'D:\Personalized Financial Dashboard\sample_bank_statement.csv')

# Preview
#print("Initial Data Sample:")
#print(df.head(5))

# Check columns (important for debugging)
#print("\nColumns:", df.columns.tolist())

# Step 2: Parse 'Date' properly
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Step 3: Check missing values
#print("\nMissing values per column:")
#print(df.isnull().sum())

# Step 4: Clean missing data
df = df.dropna(subset=['Date'])  # Remove rows with bad date
df['Merchant Category Code'] = df['Merchant Category Code'].fillna('unknown')
df['Notes'] = df['Notes'].fillna('No notes provided')

# Step 5: Clean Transaction Description (only if column exists)
if 'Transaction Description' in df.columns:
    df['Transaction Description'] = df['Transaction Description'].astype(str).str.strip().str.lower()
else:
    print("\n⚠️ Column 'Transaction Description' not found!")

# Step 6: Standardize Category
if 'Category' in df.columns:
    df['Category'] = df['Category'].astype(str).str.title()
else:
    print("\n⚠️ Column 'Category' not found!")

# Step 7: Remove duplicates
print(f"\nDuplicate rows: {df.duplicated().sum()}")
df = df.drop_duplicates()

# Step 8: Sort by Date
df = df.sort_values(by='Date').reset_index(drop=True)

# Print all unique DateTime entries
print("\nUnique DateTime entries in the dataset:")
print(df['Date'].sort_values().unique())

# Step 9: Ensure Amount is numeric
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
df = df.dropna(subset=['Amount'])

# Final check
print(f"\nCleaned Data Shape: {df.shape}")
#print(df.info())

# Show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Show cleaned sample
print("\nCleaned Data Sample:")
print(df)

# Check for uniqueness (NEW for debugging)
print("\nUnique Dates:", df['Date'].nunique())
if 'Transaction Description' in df.columns:
    print("Unique Transaction Descriptions:", df['Transaction Description'].nunique())

# Function 3:- Spending Categorization :-

# Normalize the transcription description
#If your transaction data does not include a Category column, or if it’s partially filled or incorrect, you can auto-categorize each transaction based on the text in the Transaction Description column.
df['Transaction Description'] = df['Transaction Description'].astype(str).str.strip().str.lower()

# Define keyword-category mapping
category_keywords = {
    "Groceries": ["whole foods", "walmart", "costco", "target"],
    "Utilities": ["city electric", "water utility"],
    "Electronics": ["best buy", "apple store"],
    "Entertainment": ["netflix", "spotify", "airbnb"],
    "Health": ["cvs pharmacy", "gym membership"],
    "Shopping": ["amazon", "local bookstore"],
    "Coffee & Food": ["starbucks", "mcdonald's"],
    "Transport": ["uber", "shell gas", "delta airlines"]
}

# Categorization function
def categorize_transaction(description):
    for category, keywords in category_keywords.items():
        if any(keyword in description for keyword in keywords):
            return category
    return "Others"

# Apply categorization
df['category'] = df['Transaction Description'].apply(categorize_transaction)
# Preview categorization data
print("Categorize transaction descriptions into groups if you want to analyze your spending habits, you need to group them into categories.")
print(df[['Transaction Description', 'Category']].head(20))
#print(df.head(20))

# Function 4:- Exploratory Data Analysis (EDA)

# To calculate:- Total income vs total spending, Spending by category and calculate monthly, quartely, yearly totals expense
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']).sort_values('Date')

# Calculate the key variables
total_income = df[df['Amount'] > 0]['Amount'].sum() # creates a filter for all positive values, selects only those rows from the DataFrame where the amount is greater than zero.
total_spending = df[df['Amount'] < 0]['Amount'].sum() # Filters for all negative values (expenses like groceries, bills, etc.).

spending_by_category = df[df['Amount'] < 0].groupby('category')['Amount'].sum().sort_values() #To calculate how much you spent in each category, and sort it from least to most.

df['Month'] = df['Date'].dt.to_period('M')
monthly_totals =df.groupby('Month')['Amount'].sum()

df['Quarter'] = df['Date'].dt.to_period('Q')
quarterly_totals = df.groupby('Quarter')['Amount'].sum()


df['Year'] = df['Date'].dt.year
yearly_totals = df.groupby('Year')['Amount'].sum()

# Rolling monthly average
# To calculate a rolling 30-day average of daily transaction amounts — smooth out fluctuations and spot trends.
daily_df = df.set_index('Date').resample('D').sum(numeric_only=True) # resample('D') Groups data by calendar day ('D' means daily frequency).This means if you have multiple transactions on the same day, they’ll be grouped together.
daily_df['Rolling_Monthly_Avg'] = daily_df['Amount'].rolling(window=30).mean() # creating a rolling window of 30 days
#print(df)
#print(df.head(20))

# _____________________________________ VISUALIZATIONS__________________________________________________
# 1. Total Income vs Total Spending
plt.figure(figsize=(6, 4)) # plt.figure() creates a new figure (canvas) to plot on and figsize=(6, 4) sets the width and height of the figure in inches.
plt.bar(['Income', 'Spending'], [total_income, abs(total_spending)], color=['green', 'red']) # Plot bars for income and spending with colors
plt.title('Total Income vs Total Spending') # Add title to the plot
plt.ylabel('Amount (₹)') #Label the y-axis
plt.grid(axis='y') # Add horizontal gridlines
plt.tight_layout() # Adjust layout for neatness
plt.show() #show the plot

# 2. Spending by Category
plt.figure(figsize=(8, 5))
spending_by_category.plot(kind='barh', color='purple')
plt.title('Spending by Category')
plt.xlabel('Amount (₹)')
plt.ylabel('Category')
plt.grid(True)
plt.tight_layout()
plt.show()

# Pi Chart of this function:- 2. Spending by Category
# Create pie chart for spending by category
plt.figure(figsize=(8, 6))
plt.pie(
    spending_by_category.abs(),                  # Absolute values to avoid negative amounts
    labels=spending_by_category.index,           # Category names as labels
    autopct='%1.1f%%',                           # Show percentage on the pie
    startangle=140,                              # Rotate start angle for better layout
    colors=plt.cm.Purples(range(50, 50 + len(spending_by_category) * 10, 10))  # Purple shades
)

plt.title('Spending Distribution by Category')
plt.axis('equal')  # Ensures pie is drawn as a circle
plt.tight_layout()
plt.show()

#3. Monthly Totals
plt.figure(figsize=(10, 5))
monthly_totals.plot(kind='line', marker='o', color='blue')
plt.title('Monthly Net Amounts')
plt.xlabel('Month')
plt.ylabel('Net Amount (₹)')
plt.grid(True)
plt.tight_layout()
plt.show()

# 4. Rolling 30-Day Average
plt.figure(figsize=(10, 5))
daily_df['Rolling_Monthly_Avg'].dropna().plot(color='orange')
plt.title('30-Day Rolling Monthly Average Spending')
plt.xlabel('Date')
plt.ylabel('Average Amount (₹)')
plt.grid(True)
plt.tight_layout()
plt.show()
print(df.head(20))

# Function 5:- Statistical Summaries and Trends
# We will calculate the mean, median, Standard deviation of monthly spending

# 1. Mean, Median, Standard Deviation of Monthly Spending
# Sample monthly spending data
monthly_spending = np.array([1200, 1350, 1250, 1400, 1600, 1500, 1700, 1600])

mean_spending = np.mean(monthly_spending)
median_spending = np.median(monthly_spending)
std_spending = np.std(monthly_spending) # Standard Deviation

print("Mean Spending = ", mean_spending)
print("Meadina Spending = ", median_spending)
print("Standard Deviation = ", std_spending)

# 2. Month-over-Month Percentage Change, Monthly percentage change
percent_change = np.diff(monthly_spending) / monthly_spending[:-1] * 100
print("Percentage change Month-over-Month:", percent_change)

# 3. Detect top spending categories
category_totals = df.groupby('Category')['Amount'].sum()
top_categories = category_totals.sort_values(ascending=False)
print("Top Spending Categories:\n", top_categories)

# 4.Identify Irregular Spikes or Dips
# You want to find months where your spending is unusually high or low — compared to your typical monthly spending,  Standard Deviation (std):
# Tells you how much your spending typically varies from the mean.
# Small std = your spending is stable, Large std = your spending changes a lot.

threshold = 1.5 # you can adjust this value
mean = np.mean(monthly_spending)
std = np.std(monthly_spending)

# Detect anomalies: spikes or dips more than 1.5 standard deviations from mean
anomalies = np.where(np.abs(monthly_spending - mean) > threshold * std)[0] # This line is used to detect anomalies (outliers) in the monthly_spending data. It uses NumPy to find which values deviate significantly from the mean.
print("Irregular spikes or dips found in month (0-indexed):", anomalies)

# Visual Aid - for better understanding :-
plt.plot(monthly_spending, marker = 'o', label='Monthly Spending') # marker='o': Draws a circle (o) at each data point.
plt.axhline(mean, color='green', linestyle='--', label='Mean') #plt.axhline(...): Draws a horizontal line across the plot.
plt.scatter(anomalies, monthly_spending[anomalies], color='red', label='Anomalies') # plt.scatter(x, y): Creates a scatter plot (dots only)
plt.legend() # Displays a box with labels: Monthly Spending, Mean, Anomalies.
# Add title and axis labels
plt.title("Monthly Spending with Anomalies")
plt.xlabel("Month")
plt.ylabel("Spending")
plt.grid(True)
plt.show()

df.groupby('Category')['Amount'].sum()
#print(df.head(20))

# Final Charts
fig, axs = plt.subplots(2, 2, figsize=(14, 10))

# 1. Total Income vs Total Spending
axs[0, 0].bar(['Income', 'Spending'], [total_income, abs(total_spending)], color=['green', 'red'])
axs[0, 0].set_title('Total Income vs Total Spending')
axs[0, 0].set_ylabel('Amount (₹)')
axs[0, 0].grid(axis='y')

# 2. Spending by Category
spending_by_category.plot(kind='barh', color='purple', ax=axs[0, 1])
axs[0, 1].set_title('Spending by Category')
axs[0, 1].set_xlabel('Amount (₹)')
axs[0, 1].grid(True)

# 3. Monthly Net Amounts
monthly_totals.plot(kind='line', marker='o', color='blue', ax=axs[1, 0])
axs[1, 0].set_title('Monthly Net Amounts')
axs[1, 0].set_xlabel('Month')
axs[1, 0].set_ylabel('Net Amount (₹)')
axs[1, 0].grid(True)

# 4. 30-Day Rolling Monthly Average
daily_df['Rolling_Monthly_Avg'].dropna().plot(color='orange', ax=axs[1, 1])
axs[1, 1].set_title('30-Day Rolling Monthly Average Spending')
axs[1, 1].set_xlabel('Date')
axs[1, 1].set_ylabel('Average Amount (₹)')
axs[1, 1].grid(True)

# ✅ Main title (fixes title not showing)
plt.suptitle('Personalized Financial Summary Dashboard', fontsize=16, fontweight='bold')

# ✅ Adjust layout so the title is not cut off
plt.tight_layout()
plt.subplots_adjust(top=0.92)  # Space for suptitle

plt.show()


# --- 1. Category Keywords ---
category_keywords = {
    "Groceries": ["whole foods", "walmart", "costco", "target"],
    "Utilities": ["city electric", "water utility"],
    "Electronics": ["best buy", "apple store"],
    "Entertainment": ["netflix", "spotify", "airbnb"],
    "Health": ["cvs pharmacy", "gym membership"],
    "Shopping": ["amazon", "local bookstore"],
    "Coffee & Food": ["starbucks", "mcdonald's"],
    "Transport": ["uber", "shell gas", "delta airlines"]
}

# --- 2. Categorization function ---
def categorize_transaction(description):
    description = description.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in description for keyword in keywords):
            return category
    return "Others"

# --- 3. Email Alert function with error handling ---
def send_email_alert(category, budget, spent, to_email):
    msg = MIMEText(f"Alert! You have exceeded your budget for {category}.\nBudget: ${budget}\nSpent: ${spent:.2f}")
    msg['Subject'] = f'Budget Alert: {category}'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email alert sent for category: {category}")
    except Exception as e:
        print(f"Failed to send email alert for {category}: {e}")

# --- 4. Monthly budgets ---
monthly_budgets = {
    "Groceries": 500,
    "Utilities": 150,
    "Electronics": 200,
    "Entertainment": 100,
    "Health": 100,
    "Shopping": 300,
    "Coffee & Food": 150,
    "Transport": 100,
    "Others": 100
}

# --- 5. Prepare DataFrame ---
# (Assuming df is already loaded and cleaned earlier)
df['Transaction Description'] = df['Transaction Description'].astype(str)
df['category'] = df['Transaction Description'].apply(categorize_transaction)
df['Date'] = pd.to_datetime(df['Date'])
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

# --- 6. Filter current month transactions ---
current_month = pd.Timestamp.now().month
current_year = pd.Timestamp.now().year
df_current_month = df[(df['Date'].dt.month == current_month) & (df['Date'].dt.year == current_year)]

# --- 7. Calculate spending by category ---
spending_by_category = df_current_month.groupby('category')['Amount'].sum()

print("Spending this month by category:")
print(spending_by_category)

# --- 8. Email credentials and recipient ---
EMAIL_ADDRESS = "omomomomomomomo@gmial.com"  # Your Gmail address
EMAIL_PASSWORD = "1234567878!"  # Use Gmail App Password here (do NOT share or commit real password!)
TO_EMAIL = "omomomomomomo@gmail.com"  # Recipient email address

# --- 9. Check budgets and send alerts ---
for category, budget in monthly_budgets.items():
    spent = spending_by_category.get(category, 0)
    if spent > budget:
        print(f"Alert! You have exceeded your budget for {category}. Budget: ${budget}, Spent: ${spent:.2f}")
        send_email_alert(category, budget, spent, TO_EMAIL)

# --- Optional: preview categorization ---
print("Transaction Description as per Budget")
print(df[['Transaction Description', 'category']].head(20))
print("The complete and sorted details of your Expendature:-")
#print(df.head(20))
print(df)