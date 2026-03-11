import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re 
from scipy.stats import kruskal, f_oneway, spearmanr, mannwhitneyu
import itertools

# Укажите имя файла
FILE_PATH = 'mvideo_smartphones_FINAL_CLEAN.csv' 

df = pd.read_csv(FILE_PATH, encoding='utf-8-sig')

# очистка данных от смартфонов

KNOWN_BRANDS = df[df['Производитель'] != 'смартфон']['Производитель'].unique()
pattern = '|'.join([re.escape(brand) for brand in KNOWN_BRANDS])
pattern = f'\\b({pattern})\\b'

def find_and_correct_brand(row):
    if row['Производитель'] != 'смартфон':
        return row['Производитель']
    
    match = re.search(pattern, row['Название модели'], flags=re.IGNORECASE)
    
    if match:
        found_brand = match.group(1) 
        for brand in KNOWN_BRANDS:
            if brand.lower() == found_brand.lower():
                return brand
    return row['Производитель']

df['Производитель'] = df.apply(find_and_correct_brand, axis=1)
condition_oneplus = (df['Производитель'] == 'смартфон') & (df['Название модели'].str.contains('OnePlus', case=False, na=False))
df.loc[condition_oneplus, 'Производитель'] = 'OnePlus'


# ТОП-10 брендов по количеству товаров 
top_brands_by_count = df['Производитель'].value_counts().nlargest(10).index
df_filtered_discount = df[df['Производитель'].isin(top_brands_by_count)].copy() 

# Рассчитываем медианну и определяем порядок сортировки
median_price_by_brand = df.groupby('Производитель')['Цена'].median().sort_values(ascending=False)
top_10_brands_price_order = median_price_by_brand.head(10).index
df_filtered_price = df[df['Производитель'].isin(top_10_brands_price_order)].copy()


sns.set_style("whitegrid")
plt.figure(figsize=(14, 8))

sns.boxplot(
    x='Скидка (%)', 
    y='Производитель', 
    data=df_filtered_discount, 
    palette='viridis',
    order=top_brands_by_count 
)

plt.title('Распределение скидок среди ТОП-10 производителей', fontsize=16)
plt.xlabel('Скидка', fontsize=14)
plt.ylabel('Производитель', fontsize=14)
plt.grid(axis='x') 


plt.figure(figsize=(14, 8))
sns.barplot(
    x='Цена', 
    y='Производитель', 
    data=df_filtered_price, 
    estimator='median', 
    ci=None, 
    order=top_10_brands_price_order,
    palette='magma'
)

plt.title('Медианная цена смартфонов по брендам (ТОП-10)', fontsize=16)
plt.xlabel('Медианная цена', fontsize=14)
plt.ylabel('Производитель', fontsize=14)
plt.grid(axis='x')


plt.tight_layout()
plt.show()


print(median_price_by_brand.head(10).to_string())
print("\n----------------------")
print(df.groupby('Производитель')['Скидка (%)'].median().sort_values(ascending=False).head(10).to_string())


# медианы по брендам
median_price = df.groupby('Производитель')['Цена'].median()
median_discount = df.groupby('Производитель')['Скидка (%)'].median()

# Kruskal-Wallis по скидкам 
brands = list(top_brands_by_count)  # уже есть в коде
groups = [df[df['Производитель']==b]['Скидка (%)'].dropna() for b in brands]
stat, p = kruskal(*groups)
print("Kruskal-Wallis по скидкам: stat=%.3f p=%.3e" % (stat, p))

# Корреляция медианная цена vs медианная скидка (Spearman)
common = median_price.index.intersection(median_discount.index)
rp, pp = spearmanr(median_price.loc[common], median_discount.loc[common])
print("Spearman между медианной ценой и скидкой: rho=%.3f p=%.3e" % (rp, pp))

# 4) Пост-hoc для парных сравнений скидок (Mann-Whitney с корректировкой Бонферрони)
pairs = list(itertools.combinations(brands, 2))
results = []
for a,b in pairs:
    u, pval = mannwhitneyu(df[df['Производитель']==a]['Скидка (%)'].dropna(),
                           df[df['Производитель']==b]['Скидка (%)'].dropna(),
                           alternative='two-sided')
    results.append((a,b,u,pval))
ncomp = len(results)
sig_pairs = [(a,b,u,p*ncomp) for (a,b,u,p) in results if p*ncomp < 0.05]
print("Значимые парные различия (после Bonferroni):", sig_pairs)
