# import libraries
import pandas as pd
import numpy as np
from scipy.stats import binom_test
from statsmodels.stats.proportion import proportions_ztest


# Пример с Виноградным днем. Менеджер утверждает, что 80% покупателей довольны напитком. Мы опросили 100 человек,
# 75 ответили, что напиток им нравится

# My solution
# Input data
sample_size = 100
sample_proportion = 0.75
true_population_proportion = 0.80
a = 1.96

# Output
standard_error = (sample_proportion * (1 - sample_proportion) / sample_size) ** 0.5
print('standard_error:', standard_error)
margin_error = a * standard_error
print('margin_error:', margin_error)
lower_value = sample_proportion - margin_error
upper_value = sample_proportion + margin_error
print('lower_value:', lower_value)
print('upper_value:', upper_value)
if lower_value <= true_population_proportion <= upper_value:
    print('Менеджер не врет')
else:
    print('Менеджер врет')

# Lecturer solution
sample = np.random.binomial(1, 0.8, 100)
sample_mean = np.mean(sample)
print('sample_mean:', sample_mean)
p_value = np.mean([np.random.binomial(1, 0.8, 100).mean() <= sample_proportion for i in range(10000)])
print(p_value)
print(binom_test(75, n=sample_size, p=0.8,  alternative='less'))
print(proportions_ztest(75, 100, value=0.8, alternative='smaller'))
