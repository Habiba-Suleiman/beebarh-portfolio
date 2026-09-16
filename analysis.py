import pandas as pd
 
df = pd.read_csv('data/healthcare_dataset.csv')

print(df['Billing Amount'].head(10))
print(df['Billing Amount'].dtype)

print("Shape:", df.shape)
print("\nColumn types:")
print(df.dtypes)
print("\nMissing valus per column:")
print(df.isnull().sum())
print("\nUnique values per column:")
print(df.nunique())

#---------- Cleaned Data -----------------
print("\nDuplicate rows:", df.duplicated().sum())
df = df.drop_duplicates()

df['Name'] = df['Name'].str.title()

df['Date of Admission'] = pd.to_datetime(df['Date of Admission'], dayfirst=True)
df['Discharge Date'] = pd.to_datetime(df['Discharge Date'], dayfirst=True)

df['Billing Amount'] = (
    df['Billing Amount']
    .astype(str)
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .astype(float)
)

print("\nBilling amount summary:")
print(df['Billing Amount'].describe())
print("Negative billing rows:", (df['Billing Amount'] < 0).sum())

df['Length of Stay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days

bins = [0,18,35,50,65,120]
labels = ['0-18', '19-35', '36-50','51-65', '66+']
df['Age Group'] = pd.cut(df['Age'], bins=bins, labels=labels)

df['Admission Month'] = df['Date of Admission'].dt.to_period('M').astype(str)

df.to_csv('data/cleaned_healthcare_dataset.csv', index=False)
print("\nCleaned file saved successfully!")
print("New shape:", df.shape)

#Diagnostic
bad_dates  = df[pd.to_datetime(df['Discharge Date'], errors='coerce').isna()]
print("\nRows with Unperseable Discharge Date:", len(bad_dates))
print(bad_dates[['Discharge Date']].head(10))

#---------------- Exploratory Analysis ---------------------
print("\n\n=========== DEMOGRAPHICS ===========")
print("\nAge summary:")
print(df['Age'].describe())
print("\nPatients by Age Group:")
print(df['Age Group'].value_counts().sort_index())
print("\nPatients by Gender:")
print(df['Gender'].value_counts())
print("\nCondition share within each Blood Type (%):")
print((pd.crosstab(df['Blood Type'],df['Medical Condition'], normalize='index') * 100).round(1))

print("\n\n========== CONDITIONS ===========")
print("\nCases per condition:")
print(df['Medical Condition'].value_counts())
print("\nConditions by Age Group:")
print(pd.crosstab(df['Age Group'], df['Medical Condition']))

print("\n\n=============== ADMISSIONS ================")
print("\nAdmissions per month:")
print(df.groupby('Admission Month').size())
print("\nAdmission Type counts:")
print(df['Admission Type'].value_counts())
print("\nAvg Length of Stay by Condition:")
print(df.groupby('Medical Condition')['Length of Stay'].mean().round(2))
print("\nAvg Length of Stay by Admission Type:")
print(df.groupby('Admission Type')['Length of Stay'].mean().round(2))

print("\n\n=============== FINANCIALS =================")
print("\nBilling total & average by Condition:")
print(df.groupby('Medical Condition')['Billing Amount'].agg(['sum', 'mean']).round(2))
print("\nPatients per Insurance Provider:")
print(df['Insurance Provider'].value_counts())
print("\nAvg Billing by Admission Type:")
print(df.groupby('Admission Type')['Billing Amount'].mean().round(2))

print("\n\n================= HOSPITALS & DOCTORS ==================")
print("\nTop 10 Hospitals by case count:")
print(df['Hospital'].value_counts().head(10))
print("\nTop 10 Doctors by caseload:")
print(df['Doctor'].value_counts().head(10))

print("\n\n================== OUTCOMES ===================")
print("\nTest Result distribution:")
print(df['Test Results'].value_counts())
normal_rate = (df[df['Test Results'] == 'Normal'].groupby('Medical Condition').size()
               / df.groupby('Medical Condition').size() * 100)
print("\n'Normal' result rate by condition (%):")
print(normal_rate.round(1))
print("\nMedication counts by Condition:")
print(pd.crosstab(df['Medical Condition'], df['Medication']))

print("\n\n================ OPERATIONAL ===================")
print("\nAdmissions by Day of the week:")
print(df['Date of Admission'].dt.day_name().value_counts())
print("\nAvg Room Number by Test Result:")
print(df.groupby('Test Results')['Room Number'].mean().round(1))

import matplotlib.pyplot as plt
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

import os
os.makedirs('charts', exist_ok=True)

# 1. Age distribution
fig, ax = plt.subplots(figsize=(7,4))
ax.hist(df['Age'], bins=20, color='#2E89AF', edgecolor='white')
ax.set_title('Age Distribution of Patients')
ax.set_xlabel('Age'); ax.set_ylabel('Number of Patients')
fig.savefig('charts/01_age_distribution.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 2. Gender split
fig, ax = plt.subplots(figsize=(5,4))
df['Gender'].value_counts().plot(kind='bar', ax=ax, color=['#2E89AB', "#811578"])
ax.set_title('Patients by Gender')
plt.xticks(rotation=0)
fig.savefig('charts/02_gender.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 3. Condition frequency
fig, ax = plt.subplots(figsize=(7,4))
df['Medical Condition'].value_counts().plot(kind='bar', ax=ax, color='#2E89AB')
ax.set_title('Cases per Medical Condition')
plt.xticks(rotation=20)
fig.savefig('charts/03_condition_freq.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 4. Admission trend over time
fig, ax = plt.subplots(figsize=(9,4))
df.groupby('Admission Month').size().plot(ax=ax, color='#2E89AB')
ax.set_title('Monthly Admissions Trend')
ax.set_ylabel('Admissions')
fig.savefig('charts/04_admissions_trend.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 5. Admission type pie
fig, ax = plt.subplots(figsize=(5,5))
df['Admission Type'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
ax.set_title('Admission Type Split')
ax.set_ylabel('')
fig.savefig('charts/05_admission_type.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 6. Billing by condition
fig, ax = plt.subplots(figsize=(7,4))
df.groupby('Medical Condition')['Billing Amount'].mean().plot(kind='bar', ax=ax, color="#811578")
ax.set_title('Average Billing Amount by Condition')
ax.set_ylabel('USD')
plt.xticks(rotation=20)
fig.savefig('charts/06_billing_conditions.png', dpi=150, bbox_inches='tight')
plt.close(fig)

# 7. Test result pie
fig, ax = plt.subplots(figsize=(5,5))
df['Test Results'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
ax.set_title('Test Result Distribution')
ax.set_ylabel('')
fig.savefig('charts/07_test_result.png', dpi=150, bbox_inches='tight')
plt.close(fig)

print("\nAll charts saved to the 'charts' folder!")