import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import joblib

python_data = joblib.load('artefacts/python/time_taken.joblib')
rust_data = joblib.load('artefacts/rust_parallel/time_taken.joblib')

# Create a DataFrame for easier plotting with Seaborn
df = pd.DataFrame({
    'value': python_data + rust_data,
    'distribution': ['Python'] * len(python_data) + ['Rust'] * len(rust_data)
})

# Create a DataFrame for easier plotting with Seaborn
# df = pd.DataFrame({
#     'value': python_data,
#     'distribution': ['Python'] * len(python_data)
# })

# Plotting
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='value', hue='distribution', element='step', stat='count', common_norm=False, kde=True, bins=40)

# Add vertical lines for means
mean1 = df[df['distribution'] == 'Python']['value'].mean()
mean2 = df[df['distribution'] == 'Rust']['value'].mean()

plt.axvline(mean1, color='blue', linestyle='--', label=f'Mean Python: {mean1:.2f}')
plt.axvline(mean2, color='orange', linestyle='--', label=f'Mean Rust: {mean2:.2f}')

plt.legend()
plt.title('Distribution Plot')
plt.xlabel('Seconds')
plt.ylabel('Count')

# Save the plot as a PNG file
# plt.savefig('distribution_plot.png', format='png', dpi=300)

# Show the plot
plt.show()
