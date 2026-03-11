import tkinter as tk
import pandas as pd
from tkinter import Tk, filedialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

# Глобальная переменная для хранения загруженных данных
combined_data = pd.DataFrame()

def extract_date_from_filename(filename):
    months = {
        "январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5, "июнь": 6,
        "июль": 7, "август": 8, "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12
    }
    match = re.search(r"(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь) (\d{4})", filename.lower())
    if match:
        month_name = match.group(1)
        year = int(match.group(2))
        month = months.get(month_name)
        return (year, month)
    return None

def load_excel_files():
    global combined_data
    root = Tk()
    root.withdraw()  # Скрыть главное окно

    file_paths = filedialog.askopenfilenames(
        title="Выберите файлы Excel",
        filetypes=[("Excel files", "*.xlsx;*.xls")]
    )

    if file_paths:
        # Список файлов с датами
        files_with_dates = []

        for file_path in file_paths:
            file_date = extract_date_from_filename(file_path)
            if file_date:  # Если дата успешно извлечена
                files_with_dates.append((file_path, file_date))
            else:
                print(f"Предупреждение: Не удалось определить дату для файла {file_path}. Он будет пропущен.")

        # Сортируем файлы по дате (год, месяц)
        files_with_dates.sort(key=lambda x: x[1])

        # Загружаем данные из файлов
        combined_data = pd.DataFrame()
        count = 0
        for file_path, _ in files_with_dates:
            try:
                # Загрузить файл, пропуская 11 строк
                data = pd.read_excel(file_path, skiprows=11)

                if data.shape[1] >= 4:  # Проверяем, что есть как минимум 4 столбца
                    # Преобразуем столбец D в числовой формат
                    data_d = pd.to_numeric(data.iloc[:, 3], errors='coerce')  # 'NaN' сохраняются

                    # Заменяем NaN на 1
                    data_d = data_d.fillna(1)

                    # Добавляем данные в общий DataFrame
                    combined_data = pd.concat([combined_data, data_d], ignore_index=True)
                    count += 1
            except Exception as e:
                print(f"Ошибка при загрузке файла {file_path}: {e}")

        # Печать объединенных данных
        print(combined_data.to_string())

        # Извлекаем числа из объединенных данных
        extract_numbers(combined_data, count)

def extract_numbers(data, count_exeel):
    # Извлечение чисел из DataFrame
    numbers = []

    # Проходим по всем столбцам
    for column in data.columns:
        # Получаем все числовые значения из столбца
        column_numbers = data[column].dropna().tolist()
        numbers.extend(column_numbers)

    print("Извлеченные числа:", numbers)
    # Отображаем извлеченные числа в текстовом поле
    text.insert(tk.END, "\nИзвлеченные числа:\n" + ", ".join(map(str, numbers)) + "\n")

    text.insert(tk.END, f"\nКоличество загруженных файлов: {count_exeel}\n")

    # Вызов функции для агрегирования чисел
    aggregate_numbers(numbers, count_exeel)

def plot_data(axes, x_data, y_data, consumer_type):
    # Построение графика
    line, = axes.plot(x_data, y_data, marker="o", markersize=8, linewidth=2, label=consumer_type)
    axes.set_title(f"{consumer_type}")
    axes.set_xlabel("X-axis")
    axes.set_ylabel("Y-axis")

    # Добавление аннотации для отображения значений
    annot = axes.annotate(
        "",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)

    def update_annotation(ind):
        # Обновляем текст и позицию аннотации
        x, y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"({x[ind['ind'][0]]}, {y[ind['ind'][0]]:.2f})"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.7)

    def on_hover(event):
        # Обработчик события наведения мыши
        is_visible = False
        if event.inaxes == axes:
            cont, ind = line.contains(event)
            if cont:
                update_annotation(ind)
                annot.set_visible(True)
                is_visible = True
        if not is_visible:
            annot.set_visible(False)
        # Перерисовка фигуры
        event.canvas.draw_idle()

    # Подключаем обработчик к событию мыши
    axes.figure.canvas.mpl_connect("motion_notify_event", on_hover)

def create_graph_tabs(root, aggregated_results, count_exeel):
    graph_window = tk.Toplevel(root)
    graph_window.title("Графики  с мощностью до 670 кВт")
    graph_window.geometry("+10+100")
    graph_tab = ttk.Notebook(graph_window)
    graph_tab.pack(pady=10, fill=tk.BOTH, expand=True)

    try:
        consumer_indices = {
            "Непромышленные потребители": [1],
            "Промышленные потребители": [2],
            "Торговые организации": [3]
        }

        grouped_data = {consumer_type: [] for consumer_type in consumer_indices}

        for file_index in range(count_exeel):
            for consumer_type, base_indices in consumer_indices.items():
                for base_index in base_indices:
                    index = base_index + (file_index * 10)
                    if 0 <= index < len(aggregated_results):
                        grouped_data[consumer_type].append(aggregated_results[index])
                    else:
                        print(f"Warning: Index {index} out of bounds in file {file_index + 1} for {consumer_type}. Skipping.")

        data_sets = []
        for consumer_type in consumer_indices:
            data_sets.append((range(len(grouped_data[consumer_type])), grouped_data[consumer_type]))

        for i, consumer_type in enumerate(consumer_indices):
            tab = ttk.Frame(graph_tab)
            graph_tab.add(tab, text=consumer_type)

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            grid = fig.add_gridspec(1, 1)
            axes = fig.add_subplot(grid[0, 0])

            plot_data(axes, data_sets[i][0], data_sets[i][1], consumer_type)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    except Exception as e:
        print(f"Error: {e}. Not enough data or incorrect consumer type indices in aggregated_results.")

def create_graph_tabs2(root, aggregated_results, count_exeel):
    # Создаем новое окно для графиков
    graph_window = tk.Toplevel(root)
    graph_window.title("Графики с мощностью от 670 до 10 МВт")
    screen_width = graph_window.winfo_screenwidth()
    # Устанавливаем позицию окна по центру сверху
    window_width = 600  # Можно задать размер окна
    window_height = 450
    x_position = (screen_width - window_width) // 2
    y_position = 20  # Снизу
    graph_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Создаем вкладки для графиков в новом окне
    graph_tab = ttk.Notebook(graph_window)
    graph_tab.pack(pady=10, fill=tk.BOTH, expand=True)

    try:
        consumer_indices = {
            "Непромышленные потребители": [5],
            "Промышленные потребители": [6],
            "Торговые организации": [7]
        }

        grouped_data = {consumer_type: [] for consumer_type in consumer_indices}

        for file_index in range(count_exeel):
            for consumer_type, base_indices in consumer_indices.items():
                for base_index in base_indices:
                    index = base_index + (file_index * 10)
                    if 0 <= index < len(aggregated_results):  # Проверка индекса
                        grouped_data[consumer_type].append(aggregated_results[index])
                    else:
                        print(f"Warning: Index {index} out of bounds in file {file_index + 1} for {consumer_type}. Skipping.")

        data_sets = []
        for consumer_type in consumer_indices:
            data_sets.append((range(len(grouped_data[consumer_type])), grouped_data[consumer_type]))

        for i, consumer_type in enumerate(consumer_indices):
            tab = ttk.Frame(graph_tab)
            graph_tab.add(tab, text=consumer_type)

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            axes = fig.add_subplot(111)

            plot_data(axes, data_sets[i][0], data_sets[i][1], consumer_type)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    except Exception as e:
        print(f"Error: {e}. Not enough data or incorrect consumer type indices in aggregated_results.")

def create_graph_tabs10(root, aggregated_results, count_exeel):
    # Создаем новое окно для графиков
    graph_window = tk.Toplevel(root)
    graph_window.title("Графики для максимальной мощностью свыше 10 МВт")
    screen_width = graph_window.winfo_screenwidth()
    screen_height = graph_window.winfo_screenheight()
    # Устанавливаем позицию окна по центру снизу
    window_width = 600
    window_height = 450
    x_position = (screen_width - window_width) // 2
    y_position = screen_height - window_height - 100  # Снизу
    graph_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Создаем вкладки для графиков в новом окне
    graph_tab = ttk.Notebook(graph_window)
    graph_tab.pack(pady=10, fill=tk.BOTH, expand=True)

    try:
        consumer_indices = {
            "Потребители  свыше 10 МВт": [8],
        }

        grouped_data = {consumer_type: [] for consumer_type in consumer_indices}

        for file_index in range(count_exeel):
            for consumer_type, base_indices in consumer_indices.items():
                for base_index in base_indices:
                    index = base_index + (file_index * 10)
                    if 0 <= index < len(aggregated_results):  # Проверка индекса
                        grouped_data[consumer_type].append(aggregated_results[index])
                    else:
                        print(f"Warning: Index {index} out of bounds in file {file_index + 1} for {consumer_type}. Skipping.")

        data_sets = []
        for consumer_type in consumer_indices:
            data_sets.append((range(len(grouped_data[consumer_type])), grouped_data[consumer_type]))

        for i, consumer_type in enumerate(consumer_indices):
            tab = ttk.Frame(graph_tab)
            graph_tab.add(tab, text=consumer_type)

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            axes = fig.add_subplot(111)

            plot_data(axes, data_sets[i][0], data_sets[i][1], consumer_type)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    except Exception as e:
        print(f"Error: {e}. Not enough data or incorrect consumer type indices in aggregated_results.")

def create_graph_tabsall(root, aggregated_results, count_exeel):
    # Создаем новое окно для графиков
    graph_window = tk.Toplevel(root)
    graph_window.title("Графики всего отпущено")
    graph_window.geometry("+1400+500")
    # Создаем вкладки для графиков в новом окне
    graph_tab = ttk.Notebook(graph_window)
    graph_tab.pack(pady=10, fill=tk.BOTH, expand=True)

    try:
        consumer_indices = {
            "Всего отпущено": [9],
        }

        grouped_data = {consumer_type: [] for consumer_type in consumer_indices}

        for file_index in range(count_exeel):
            for consumer_type, base_indices in consumer_indices.items():
                for base_index in base_indices:
                    index = base_index + (file_index * 10)
                    if 0 <= index < len(aggregated_results):  # Проверка индекса
                        grouped_data[consumer_type].append(aggregated_results[index])
                    else:
                        print(f"Warning: Index {index} out of bounds in file {file_index + 1} for {consumer_type}. Skipping.")

        data_sets = []
        for consumer_type in consumer_indices:
            data_sets.append((range(len(grouped_data[consumer_type])), grouped_data[consumer_type]))

        for i, consumer_type in enumerate(consumer_indices):
            tab = ttk.Frame(graph_tab)
            graph_tab.add(tab, text=consumer_type)

            fig = plt.Figure(figsize=(5, 4), dpi=100)
            axes = fig.add_subplot(111)

            plot_data(axes, data_sets[i][0], data_sets[i][1], consumer_type)

            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    except Exception as e:
        print(f"Error: {e}. Not enough data or incorrect consumer type indices in aggregated_results.")

def aggregate_numbers(numbers, count_exeel):
    index2 = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    aggregated_results = []
    for file_index in range(count_exeel):
        for i in range(len(index2)):
            if index2[i] < len(numbers):
                aggregated_results.append(numbers[index2[i]])
            else:
                aggregated_results.append(0)

        print(f"After index2 processing in iteration {file_index + 1}: {aggregated_results}")

        index2 = [i + 50 for i in index2]

    create_graph_tabs(root, aggregated_results, count_exeel)
    create_graph_tabs2(root, aggregated_results, count_exeel)
    create_graph_tabs10(root, aggregated_results, count_exeel)
    create_graph_tabsall(root, aggregated_results, count_exeel)

# Создаем главное окно
root = tk.Tk()
root.title("Графики для Excel")

# Создаем виджет Notebook для основных вкладок
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Устанавливаем минимальный размер окна
root.minsize(width=300, height=200)

# Получаем размеры экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Получаем размеры окна
window_width = 900
window_height = 700

# Рассчитываем координаты для размещения окна по центру
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)

# Устанавливаем размер и позицию окна
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Создаем первую вкладку для загрузки Excel файлов
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Загрузка файлов Excel")

# Создаем кнопку для загрузки файлов в первой вкладке
load_button = tk.Button(tab1, text="Загрузка файлов", command=load_excel_files)
load_button.pack(pady=10)

# Создаем текстовое поле для отображения данных в первой вкладке
text = tk.Text(tab1, wrap=tk.WORD, width=50, height=20)
text.pack(pady=10)

# Запускаем главный цикл приложения
root.mainloop()
