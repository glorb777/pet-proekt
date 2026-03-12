if (!require("pacman")) install.packages("pacman")
pacman::p_load(e1071, nortest, psych, ggplot2, cluster, factoextra, 
               ppcor, corrplot, ggpubr, gridExtra, GGally, scales)

# Загрузка через диалоговое окно
path <- file.choose()
df_raw <- read.csv(path, header = TRUE, sep = ",", dec = ".", na.strings = c("NA", "", ">"))

# Очистка пустых значений
cat("--- ПРОТОКОЛ ПРЕДОБРАБОТКИ ---\n")
cat("Строк изначально:", nrow(df_raw), "\n")
df <- na.omit(df_raw)
cat("Строк после удаления NA:", nrow(df), "\n")

# Определение переменных (согласно вашему списку)
quant_vars <- c("Price.USD.", "square_feet", "Bedrooms", "Bathrooms", "House_Age")
cat_vars <- c("Location_rating")
df$Location_rating <- as.factor(df$Location_rating)

#-------------------------------------
# 1. ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ И ВЫБРОСЫ 
#-------------------------------------

# 1.1 Здравый смысл: Фильтрация невозможных значений
df <- df[df$Price.USD. > 0 & df$square_feet > 0 & df$Bedrooms > 0, ]

# 1.2 Анализ гистограмм и 1.3 Ящичковых диаграмм
for(v in quant_vars) {
  p1 <- ggplot(df, aes_string(x=v)) + geom_histogram(fill="steelblue", bins=30) + labs(title=paste("Гистограмма:", v))
  p2 <- ggplot(df, aes_string(y=v)) + geom_boxplot(fill="darkorange") + labs(title=paste("Boxplot:", v))
  grid.arrange(p1, p2, ncol=2)
}

# 1.4 Критерий Ирвина (для выявления резких скачков в упорядоченных данных)
irwin_detect <- function(x) {
  x_s <- sort(x)
  lambda <- diff(x_s) / sd(x_s)
  return(data.frame(Val=x_s[-1], Lambda=lambda))
}
irwin_res <- irwin_detect(df$Price.USD.)
plot(irwin_res$Lambda, type="l", main="Критерий Ирвина (Price)", ylab="Lambda")
abline(h=1.3, col="red", lty=2) # Порог выброса

#-------------------------------------------
# 2. ОПИСАТЕЛЬНЫЕ СТАТИСТИКИ И ОДНОРОДНОСТЬ 
#-------------------------------------------

# 1. Функция для моды (оставляем твою, она рабочая)
get_mode <- function(x) { 
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))] 
}

# 2. Создаем чистую таблицу статистик, чтобы избежать ошибок с названиями колонок
# Это гарантирует, что все колонки (mean, var, skew и т.д.) будут существовать
stats_list <- lapply(df[, quant_vars], function(x) {
  data.frame(
    mean     = mean(x),
    var      = var(x),
    sd       = sd(x),
    mode     = get_mode(x),
    median   = median(x),
    Q1       = quantile(x, 0.25),
    Q3       = quantile(x, 0.75),
    cv       = (sd(x) / mean(x)) * 100
  )
})

# Собираем список в одну таблицу
stats_main <- do.call(rbind, stats_list)
rownames(stats_main) <- quant_vars

# 3. Вывод таблицы количественных переменных
cat("\n--- ТАБЛИЦА ОПИСАТЕЛЬНЫХ СТАТИСТИК (КОЛИЧЕСТВЕННЫЕ) ---\n")
print(round(stats_main, 3))

# 4. Проверка однородности (Пункт 4.3)
cat("\n--- АНАЛИЗ ОДНОРОДНОСТИ ДАННЫХ ---\n")
homogeneity <- data.frame(
  Variable = rownames(stats_main),
  CV = stats_main$cv,
  Conclusion = ifelse(stats_main$cv < 33, "Однородны (CV < 33%)", "Неоднородны")
)
print(homogeneity)

# 5. Статистика для качественных переменных
cat("\n--- АНАЛИЗ КАЧЕСТВЕННЫХ ПЕРЕМЕННЫХ ---\n")
# Для качественных переменных лучшая статистика - это частотная таблица и мода
cat("Мода для Location_rating:", get_mode(df$Location_rating), "\n")
print(table(df$Location_rating))

# 6. Графики для качественных переменных (2 разных графика)
# График 1: Столбчатый (Частоты)
g1 <- ggplot(df, aes(x=Location_rating, fill=Location_rating)) + 
  geom_bar() + 
  geom_text(stat='count', aes(label=..count..), vjust=-0.5) + # Добавим подписи цифр
  theme_minimal() + 
  labs(title="Частотный анализ рейтинга")

# График 2: Круговой (Доли)
g2 <- ggplot(df, aes(x="", fill=Location_rating)) + 
  geom_bar(width=1) + 
  coord_polar("y") + 
  theme_void() + 
  labs(title="Долевое распределение")

grid.arrange(g1, g2, ncol=2)

#---------------------------
# 3. ПРОВЕРКА НОРМАЛЬНОСТИ 
#---------------------------

for(v in quant_vars) {
  # a. Гистограммы с наложением норм. распределения
  p_norm <- ggplot(df, aes_string(x=v)) + 
    geom_histogram(aes(y=..density..), fill="grey80") +
    stat_function(fun = dnorm, args = list(mean = mean(df[[v]]), sd = sd(df[[v]])), color = "red", size=1) +
    labs(title=paste("Нормальность:", v))
  
  # b. Квантиль-Квантиль (Q-Q)
  p_qq <- ggqqplot(df[[v]], title = paste("Q-Q Plot:", v))
  grid.arrange(p_norm, p_qq, ncol=2)
  
  # e. Критерии нормальности (Шапиро-Уилк и Лиллиефорс)
  cat("\nТесты для", v, ":\n")
  # Для Шапиро берем срез, если выборка > 5000
  print(shapiro.test(df[[v]][1:min(nrow(df), 5000)]))
  print(lillie.test(df[[v]]))
}

#--------------------------
# 4. КЛАСТЕРНЫЙ АНАЛИЗ 
#--------------------------

# Масштабирование
df_sc <- scale(df[, quant_vars])

# Обоснование числа кластеров (Метод локтя)
fviz_nbclust(df_sc, kmeans, method = "wss") + labs(title="Обоснование числа кластеров")

k_opt <- 4 # Выберите оптимальное на основе графика выше
km <- kmeans(df_sc, centers = k_opt, nstart = 25)
df$cluster <- as.factor(km$cluster)

# Проверка нормальности внутри кластеров
for(i in 1:k_opt) {
  cat("\nНормальность Price в Кластере", i, ":\n")
  print(shapiro.test(df$Price.USD.[df$cluster == i][1:min(sum(df$cluster==i), 5000)]))
}

#----------------------------
# 5. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ 
#----------------------------

for(i in 1:k_opt) {
  cat("\n\n################ АНАЛИЗ КЛАСТЕРА №", i, "################\n")
  c_df <- df[df$cluster == i, quant_vars]
  
  # Корреляционная матрица и тепловая карта
  cor_res <- corr.test(c_df)
  corrplot(cor_res$r, p.mat = cor_res$p, sig.level = 0.05, method="color", 
           addCoef.col = "black", title=paste("Кластер", i), mar=c(0,0,1,0))
  
  # Частная корреляция
  cat("Частная корреляция (p-values):\n")
  try(print(pcor(c_df)$p.value))
  
  # Ранговый Спирмен (Location vs Quant)
  cat("Спирмен (Качественная vs Количественные):\n")
  for(qv in quant_vars) {
    sp <- cor.test(as.numeric(df$Location_rating[df$cluster==i]), c_df[[qv]], method="spearman")
    cat("Location vs", qv, ": p-val =", sp$p.value, "\n")
  }
  
  # Множественный коэффициент корреляции (R)
  # Берем Price как зависимую переменную
  model <- lm(Price.USD. ~ ., data=c_df)
  mult_r <- sqrt(summary(model)$r.squared)
  cat("Множественный R для Price:", mult_r, "Значимость p:", 
      pf(summary(model)$fstatistic[1], summary(model)$fstatistic[2], 
         summary(model)$fstatistic[3], lower.tail=F), "\n")
}
#----------------------------
# 5. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ (ИСПРАВЛЕННЫЙ)
#----------------------------

for(i in 1:k_opt) {
  cat("\n\n################ АНАЛИЗ КЛАСТЕРА №", i, "################\n")
  
  # 1. Берем данные текущего кластера
  c_df <- df[df$cluster == i, quant_vars]
  
  # 2. ПРОВЕРКА НА КОНСТАНТЫ: Оставляем только те колонки, где значения меняются
  # (Дисперсия не равна 0)
  varying_cols <- apply(c_df, 2, function(x) sd(x, na.rm = TRUE) > 0)
  
  # Если есть колонки с нулевой дисперсией, выводим предупреждение
  if(any(!varying_cols)) {
    cat("Внимание: переменные", names(c_df)[!varying_cols], 
        "в кластере", i, "имеют одинаковые значения и исключены из матрицы.\n")
    c_df_filtered <- c_df[, varying_cols]
  } else {
    c_df_filtered <- c_df
  }

  # 3. Расчет корреляции только для вариативных данных
  if(ncol(c_df_filtered) > 1) {
    cor_res <- corr.test(c_df_filtered)
    
    # Визуализация
    corrplot(cor_res$r, 
             p.mat = cor_res$p, 
             sig.level = 0.05, 
             method="color",  
             addCoef.col = "black", 
             title=paste("Кластер", i, "(только значимые связи)"), 
             mar=c(0,0,1,0))
    
    # Частная корреляция
    cat("Частная корреляция (p-values):\n")
    try(print(pcor(c_df_filtered)$p.value))
  } else {
    cat("В кластере слишком мало вариативных переменных для анализа корреляции.\n")
  }
  
  # 4. Ранговый Спирмен (Location vs Quant) - здесь используем исходный c_df
  cat("Спирмен (Качественная vs Количественные):\n")
  for(qv in quant_vars) {
    # Проверка на дисперсию и для Спирмена, чтобы не было ошибок
    if(sd(c_df[[qv]]) > 0) {
      sp <- cor.test(as.numeric(df$Location_rating[df$cluster==i]), c_df[[qv]], method="spearman")
      cat("Location vs", qv, ": p-val =", round(sp$p.value, 4), "\n")
    } else {
      cat("Location vs", qv, ": невозможно рассчитать (константное значение)\n")
    }
  }
}