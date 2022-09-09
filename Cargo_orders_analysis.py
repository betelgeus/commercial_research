# Main questions:
# What factors have a significant impact on the cost of the order?
# What factors affect make order?

# Process followed:
# 1. Import libraries
# 2. Import and read dataset
# 3. Clean dataset
# 4. Do EDA (exploratory data analysis)
# 5. Do one-way ANOVA tests
# 6. Do the two-way ANOVA tests

# 1. Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols

# 2. Import and read dataset
file_path = '/Users/mitya/Desktop/orders.csv'
df = pd.read_csv(file_path, header=None, sep='|', quotechar='§')

# 3. Clean dataset
# We need to clean the data: drop the first row and move column labels to header
# We set the column labels to equal the values in the 1st row (index location 0):
df.columns = df.iloc[0]

# Then we drop the 1st row using iloc
# We will save the new dataset as df_cleaned and will use this dataset from the rest of the operations
df_cleaned = df.iloc[pd.RangeIndex(len(df)).drop(0)]

# We convert the 'total' column data to numeric:
df_cleaned.total = pd.to_numeric(df_cleaned['total'], errors='coerce')
# Convert the 'distance' column data to numeric:
df_cleaned.distance = pd.to_numeric(df_cleaned['distance'], errors='coerce')
# Convert the 'duration' column data to numeric:
df_cleaned.duration = pd.to_numeric(df_cleaned['duration'], errors='coerce')

# Leave orders that are interesting for research:
df_cleaned = df_cleaned[df_cleaned.status_id != 'NEW']
df_cleaned = df_cleaned[df_cleaned.status_id != 'CALC']


# Group orders by cargo count
df_cleaned_cargo_count_0 = df_cleaned[df_cleaned.cargo_count == '0']
df_cleaned_cargo_count_1 = df_cleaned[df_cleaned.cargo_count == '1']
df_cleaned_cargo_count_2 = df_cleaned[df_cleaned.cargo_count == '2']
df_cleaned_cargo_count_3 = df_cleaned[df_cleaned.cargo_count == '3']
df_cleaned_cargo_count_4 = df_cleaned[df_cleaned.cargo_count == '4']

# 4. Do EDA (exploratory data analysis)
# Find outliers using boxplot
# df_cleaned.boxplot('total', by='status_id', figsize=(12, 8), grid=True)
# df_cleaned.boxplot('total', by='cargo_count', figsize=(12, 8), grid=True)
# df_cleaned.boxplot('total', by='passengers_count', figsize=(12, 8), grid=True)
# plt.show()

# Delete outliers:
# df_cleaned = df_cleaned[df_cleaned.total <= 1000]
# df_cleaned = df_cleaned[df_cleaned.distance <= 15000]

# Check the result
# df_cleaned.boxplot('total', by='status_id', figsize=(12, 8), grid=True)
# df_cleaned.boxplot('total', by='cargo_count', figsize=(12, 8), grid=True)
# df_cleaned.boxplot('total', by='passengers_count', figsize=(12, 8), grid=True)
# df_cleaned.boxplot('distance', by='status_id', figsize=(12, 8), grid=True)
# plt.show()

# Let's see how orders cost influenced by cargo count, passengers count, order status, duration via pointplot
# First pair cargo count:passengers count
# sns.set()
# sns.pointplot(data=df_cleaned, x='passengers_count', y='total', hue='cargo_count', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()
# We see that passengers count not affect the cost of the order.

# Next pair order status:passengers count
# sns.set()
# sns.pointplot(data=df_cleaned, x='status_id', y='total', hue='passengers_count', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()
# We see that order status have a strong influence on the cost of the order, also we see that passengers count
# began to significantly influence. Our hypothesis is that the cargo count affects the passengers count,
# and this, in turn, affects the cost of the order.

# Next pair order status:cargo count
# sns.set()
# sns.pointplot(data=df_cleaned, x='status_id', y='total', hue='cargo_count', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()
# We see that cargo count affect the cost of the order. Order status also affects the cost,
# especially in orders with the "Delete" status and the count of loaders: 0, 1, 2.

# Next pair order status:duration
# sns.set()
# sns.pointplot(data=df_cleaned, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()

# Next pair cargo_count:duration
# sns.set()
# sns.pointplot(data=df_cleaned, x='duration', y='total', hue='cargo_count', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()

# Last pair passengers_count:duration
# sns.set()
# sns.pointplot(data=df_cleaned, x='duration', y='total', hue='passengers_count', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.show()
# Intermediate conclusions:
# Strong affects: duration, cargo count.
# Order status. there is an influence, but it depends on other factors.
# No affects: passengers count

# Pair duration:status_id group by cargo count
# sns.set()
# sns.pointplot(data=df_cleaned_cargo_count_0, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.title('0 грузчиков', fontsize=16)
# plt.show()
# sns.pointplot(data=df_cleaned_cargo_count_1, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.title('1 грузчик', fontsize=16)
# plt.show()
# sns.pointplot(data=df_cleaned_cargo_count_2, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.title('2 грузчика', fontsize=16)
# plt.show()
# sns.pointplot(data=df_cleaned_cargo_count_3, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.title('3 грузчика', fontsize=16)
# plt.show()
# sns.pointplot(data=df_cleaned_cargo_count_4, x='duration', y='total', hue='status_id', dodge=True, capsize=.1, errwidth=1, palette='colorblind')
# plt.title('4 грузчика', fontsize=16)
# plt.show()

# 5. Let's do the one-way ANOVA tests.
# Create first samples set group be cargo and passengers count. The null hypothesis that samples have the same means
# Delete outliers:
df_cleaned = df_cleaned[df_cleaned.duration <= 3]
# Create groups:
cargo_0_passengers_0 = df_cleaned[(df_cleaned['cargo_count'] == '0') & (df_cleaned['passengers_count'] == '0')]["total"]
print('cargo_0_passengers_0 mean:', cargo_0_passengers_0.mean())
cargo_1_passengers_0 = df_cleaned[(df_cleaned['cargo_count'] == '1') & (df_cleaned['passengers_count'] == '0')]["total"]
print('cargo_1_passengers_0 mean:', cargo_1_passengers_0.mean())
cargo_2_passengers_0 = df_cleaned[(df_cleaned['cargo_count'] == '2') & (df_cleaned['passengers_count'] == '0')]["total"]
print('cargo_2_passengers_0 mean:', cargo_2_passengers_0.mean())
cargo_4_passengers_0 = df_cleaned[(df_cleaned['cargo_count'] == '4') & (df_cleaned['passengers_count'] == '0')]["total"]
print('cargo_4_passengers_0 mean:', cargo_4_passengers_0.mean())

cargo_1_passengers_1 = df_cleaned[(df_cleaned['cargo_count'] == '1') & (df_cleaned['passengers_count'] == '1')]["total"]
print('cargo_1_passengers_1 mean:', cargo_1_passengers_1.mean())
cargo_2_passengers_1 = df_cleaned[(df_cleaned['cargo_count'] == '2') & (df_cleaned['passengers_count'] == '1')]["total"]
print('cargo_2_passengers_1 mean:', cargo_2_passengers_1.mean())

cargo_2_passengers_2 = df_cleaned[(df_cleaned['cargo_count'] == '2') & (df_cleaned['passengers_count'] == '2')]["total"]
print('cargo_2_passengers_2 mean:', cargo_2_passengers_2.mean())
cargo_4_passengers_2 = df_cleaned[(df_cleaned['cargo_count'] == '4') & (df_cleaned['passengers_count'] == '2')]["total"]
print('cargo_4_passengers_2 mean:', cargo_4_passengers_2.mean())
cargo_3_passengers_3 = df_cleaned[(df_cleaned['cargo_count'] == '3') & (df_cleaned['passengers_count'] == '3')]["total"]
print('cargo_3_passengers_3 mean:', cargo_3_passengers_3.mean())

# Find F critical value
# Calculate Degree of freedom between groups (count of groups minus 1)
df_between = 9 - 1
# Calculate Degree of freedom within group (count of observations minus count of groups)
df_within = len(cargo_0_passengers_0) + len(cargo_1_passengers_0) + len(cargo_1_passengers_1)\
            + len(cargo_2_passengers_0) + len(cargo_2_passengers_1) + len(cargo_2_passengers_2) \
            + len(cargo_3_passengers_3) + len(cargo_4_passengers_0) + len(cargo_4_passengers_2) - 9
# Significance level is 0.05
sign_level = 1 - .05

f_critical_value = stats.f.ppf(q=sign_level, dfn=df_between, dfd=df_within)
print('f_critical_value:', f_critical_value)

# Find F and P values
print("Results for all groups", stats.f_oneway(cargo_0_passengers_0, cargo_1_passengers_0, cargo_1_passengers_1,
                                               cargo_2_passengers_0, cargo_2_passengers_1, cargo_2_passengers_2,
                                               cargo_3_passengers_3, cargo_4_passengers_0, cargo_4_passengers_2))
# Intermediate conclusions:
# Result F critical value: 1.9427521888817838, F value: 2.534611657754996, P value: 0.009572721500156237,
# reject the null hypothesis

# 6. Let's do the two-way ANOVA tests.
# Find F and P values, the sum_sq, mean_sq and df using two-way analysis of variance
# cargo_count+passengers_count
expr_lm = ols('total ~ cargo_count:passengers_count', data=df_cleaned).fit()
table_1 = sm.stats.anova_lm(expr_lm, type=2)
print(table_1)

expr_lm = ols('total ~ cargo_count*passengers_count', data=df_cleaned).fit()
table_2 = sm.stats.anova_lm(expr_lm, type=2)
print(table_2)
# Intermediate conclusions:
# sum_sq for Counts is SSB (2190384, 31146.31)
# sum_sq for Residual is SSW (232344100)
# We find significant differences within groups
# Passengers count. F value: 0.095177  P value: 0.962717
# Passengers count not make significant difference

# cargo_count+status_id
expr_lm = ols('total ~ cargo_count*status_id', data=df_cleaned).fit()
table_3 = sm.stats.anova_lm(expr_lm, type=2)
print(table_3)
# Intermediate conclusions:
# cargo_count and status_id have strong affects
