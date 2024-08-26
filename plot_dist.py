import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import joblib

python_data = joblib.load('artefacts/python/time_taken.joblib')
rust_parallel_data = joblib.load('artefacts/rust_parallel/time_taken.joblib')
rust_single_data = joblib.load('artefacts/rust_single/time_taken.joblib')

df = pd.DataFrame({
    'value': python_data + rust_parallel_data + rust_single_data,
    'distribution': ['Python'] * len(python_data) + ['Rust_parallel'] * len(rust_parallel_data) + ['Rust_single'] * len(rust_single_data)
})

# df = pd.DataFrame({
#     'value': python_data + rust_single_data,
#     'distribution': ['Python'] * len(python_data) + ['Rust_single'] * len(rust_single_data)
# })

# df = pd.DataFrame({
#     'value': python_data,
#     'distribution': ['Python'] * len(python_data)
# })

plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='value', hue='distribution', element='step', stat='count', common_norm=False, kde=True, bins=20)

distributions = {
    'Python': 'blue',
    'Rust_single': 'green',
    'Rust_parallel': 'orange'
}

for dist, color in distributions.items():
    mean = df[df['distribution'] == dist]['value'].mean()
    stddev = df[df['distribution'] == dist]['value'].std()
    plt.axvline(mean, color=color, linestyle='--', label=f'Mean {dist}: {mean:.2f}, Stddev: {stddev:.2f}')

ax = plt.gca()  
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.legend(loc='upper right')

plt.xlabel('Seconds', fontweight='bold')
plt.ylabel('Count', fontweight='bold')

# plt.savefig('distribution_plot.png', format='png', dpi=300)

plt.show()
