import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import StackingRegressor
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from sklearn import metrics

df_test = pd.read_csv(r"C:\Users\glebt\Downloads\test.csv")
df_train = pd.read_csv(r"C:\Users\glebt\Downloads\train.csv")
df_train = df_train.dropna(subset=["price", "rrp", "paymentMethod", "productGroup", "voucherAmount"])

df_train = df_train[df_train["rrp"] > 0]
df_test = df_test[df_test["rrp"] > 0]
df_train = df_train[df_train["price"] > 0]
df_test = df_test[df_test["price"] > 0]
df_train = df_train[df_train["price"] <= df_train["rrp"] * 1.3]
df_test = df_test[df_test["price"] <= df_test["rrp"] * 1.3]

y_col = "price"
x_col = ["rrp", "voucherAmount"]

df_train["is_train"] = 1
df_test["is_train"] = 0

df_all = pd.concat([df_train, df_test], ignore_index=True)
df_all['orderDate'] = pd.to_datetime(df_all['orderDate'])
df_all['order_month'] = df_all['orderDate'].dt.month
df_all['order_week'] = df_all['orderDate'].dt.dayofweek
df_all['order_year'] = df_all['orderDate'].dt.year
x_col += ['order_month', 'order_week', 'order_year']

df_all = pd.get_dummies(df_all, columns=["paymentMethod"], drop_first=True)
x_col = x_col + [col for col in df_all.columns if col.startswith('paymentMethod_')]
df_all = pd.get_dummies(df_all, columns=["productGroup"], drop_first=True)
x_col = x_col + [col for col in df_all.columns if col.startswith('productGroup')]

df_train = df_all[df_all["is_train"] == 1]
df_test = df_all[df_all["is_train"] == 0]

X_train_df = df_train[x_col]
y_train = df_train[y_col]
X_test_df = df_test[x_col]
y_test = df_test[y_col]

y_train_log = np.log1p(y_train)
y_test_log_for_eval = np.log1p(y_test)

scaler = MinMaxScaler()
X_train_norm = scaler.fit_transform(X_train_df)
X_test_norm = scaler.transform(X_test_df)

model = StackingRegressor(
    estimators=[
        ('rf', RandomForestRegressor()),
        ("lm", LinearRegression()),
        ('xgb', XGBRegressor()),
        ('knn', KNeighborsRegressor()),
    ],
    final_estimator=RidgeCV()
)
model.fit(X_train_norm, y_train_log)
y_pred_log = model.predict(X_test_norm)
y_pred_st = np.expm1(y_pred_log)
MAE_stack = metrics.mean_absolute_error(y_test, y_pred_st)
RMSE_stack = metrics.mean_squared_error(y_test, y_pred_st) ** 0.5
r2_stack = metrics.r2_score(y_test, y_pred_st)
print(f"Стэкинг модель: R² = {round(r2_stack, 3)}, MAE = {round(MAE_stack, 3)}, RMSE = {round(RMSE_stack, 3)}")