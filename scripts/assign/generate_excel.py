import pandas as pd

# Read the input file
with open('substance_portion.txt', 'r') as file:
    lines = [line.strip() for line in file if line.strip()]

# Prepare the data
records = []
current_individual = None

for line in lines:
    if not line.startswith('Amount:') and not line.startswith('Unit:'):
        current_individual = line
    elif line.startswith('Amount:'):
        amount = line.replace('Amount:', '').strip()
    elif line.startswith('Unit:'):
        unit = line.replace('Unit:', '').strip()
        # Once we have both amount and unit, add a record
        records.append({
            'Individual': current_individual,
            'Class': 'SubstancePortion',
            'Amount': amount,
            'Unit': unit
        })

# Create a DataFrame
df = pd.DataFrame(records)

# Save to CSV
csv_path = 'data/substance_portion.csv'
df.to_csv(csv_path, index=False)

# Save to Excel
excel_path = 'data/substance_portion.xlsx'
df.to_excel(excel_path, index=False)

print(f"CSV file saved to {csv_path}")
print(f"Excel file saved to {excel_path}")
