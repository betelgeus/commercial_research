# Import libraries
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind


# ШАГИ
# 1. Определяем цели, метрики и  размер выборки
# 2. EDA (exploratory data analysis)
# 3. Находим отклонения при отсутствии изменений с помощью AA-теста
# 4. Собираем данные
# 5. Проводим анализ данных

# 1. Определяем размер выборки
# Формула расчета размеры выборки зависит от типа распределения
# Пример. AB тест конверсии. Бинарный результат (конверсия есть или ее нет), биномиальное распределение Бернули,
# используем формулу N = p * (1 - p) * (a / mde) ** 2 (mde - minimum detectable effect) вместо mde может
# использоваться E (acceptable margin of error)
# * Формула упрощенная и не учитывает мощности
# p — текущий уровень конверсии
pop_prop = 0.0069
# a — пороговый уровень статистической значимости
a = 1.96
# mde — изменение в конверсии, которое мы хотим обнаружить
mde = 0.0005
N = pop_prop * (1 - pop_prop) * (a / mde) ** 2
print('count of observation:', round(N))

# 2. EDA
sample = [0.0055, 0.0077, 0.0092, 0.0094, 0.0038, 0.0046, 0.0061, 0.0077, 0.0056, 0.0071, 0.0062, 0.0056, 0.0053, 0.0043, 0.008, 0.0059, 0.0074, 0.0093, 0.0072, 0.0074, 0.0077, 0.0068, 0.0064, 0.0078, 0.0099, 0.0099, 0.0089, 0.0041, 0.0062, 0.0069]
st_dev = np.std(sample)
print('st_dev:', st_dev)

# Проверяем распределение на нормальность
plt.hist(sample)
plt.show()
stats.probplot(sample, dist="norm", plot=plt)
plt.show()

# 3. АА тест.Особенность множественного сравнения гипотез с использованием t-теста. При множественном сравнении есть
# вероятность получить подтверждение альтернавтиной гипотезы, хотя она неверна. Вероятность будет примерно равна
# заданному уровню p-value проверяем p-value на нормальном распределении
p_value = []
cnt = 0
iteration = 1000
for _ in range(iteration):
    normal_dist_1 = np.random.normal(pop_prop, st_dev, 10000).tolist()
    normal_dist_2 = np.random.normal(pop_prop, st_dev, 10000).tolist()
    result = ttest_ind(normal_dist_1, normal_dist_2)
    p_value.append(result.pvalue)
    if result.pvalue < 0.05:
        cnt += 1
print('AA test probability:', cnt / iteration)
plt.hist(p_value)
plt.show()
# Вывод: даже при нормальном распределении будут встречаться отклонения, которые подтвердять неверную
# альтернативную гипотезу

# 4. Собираем данные
p_value = []
cnt = 0
control_sample_means_distribution = []
treatment_sample_means_distribution = []
conversion_uplift = 0.0003
iteration = 1000
for _ in range(iteration):
    control_sample = np.random.normal(pop_prop, st_dev, 1000).tolist()
    treatment_sample = np.random.normal(pop_prop + conversion_uplift, st_dev, 1000).tolist()
    control_sample_means_distribution += [np.mean(control_sample)]
    treatment_sample_means_distribution += [np.mean(treatment_sample)]
    result = ttest_ind(control_sample, treatment_sample)
    p_value.append(result.pvalue)
    if result.pvalue < 0.05:
        cnt += 1

# 5. Проводим анализ данных
print('AB test probability:', cnt / iteration)
plt.hist(p_value)
plt.show()
sns.kdeplot(control_sample_means_distribution)
sns.kdeplot(treatment_sample_means_distribution)
plt.show()
