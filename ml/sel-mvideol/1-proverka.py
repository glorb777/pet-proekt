import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors
import re

# имя файла
FILE_PATH = "mvideo_smartphones_FINAL_CLEAN.csv" 

# Загрузка данных
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

# исправление оставшихся строк
condition_oneplus = (df['Производитель'] == 'смартфон') & (df['Название модели'].str.contains('OnePlus', case=False, na=False))
df.loc[condition_oneplus, 'Производитель'] = 'OnePlus'

#стиль
sns.set_style("whitegrid")

# 2. Построение диаграммы
plt.figure(figsize=(16, 10))

# отображени зависимости RAM от Цены
scatter = sns.scatterplot(
    x='RAM (ГБ)', 
    y='Цена', 
    data=df, 
    hue='Производитель', 
    palette='tab20', 
    s=120, 
    alpha=0.7
)

labels = [
    f"Производитель: {row['Производитель']}\n"
    f"Модель: {row['Название модели']}\n"
    f"RAM: {row['RAM (ГБ)']} ГБ\n"
    f"Цена: {row['Цена']} руб."
    for index, row in df.iterrows()
]

mplcursors.cursor(scatter.collections, hover=True).connect(
    "add", lambda sel: sel.annotation.set_text(labels[sel.index])
)

correlation_ram = df['RAM (ГБ)'].corr(df['Цена'])

print(f"\nКоэффициент корреляции между RAM и Ценой: {correlation_ram:.2f}")

plt.title('Зависимость цены смартфона от RAM', fontsize=16)
plt.xlabel('Объем RAM', fontsize=14)
plt.ylabel('Цена', fontsize=14)
plt.grid(True)
plt.legend(title='Производитель', loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

plt.tight_layout()
plt.show()