# ИСАДИЧЕВА ДАРЬЯ, ДПИ22-1

import random
import multiprocessing
import os
import time

def calculate_element_and_save(index, matrix_a, matrix_b, temp_file):
    """
    Вычисляет один элемент результирующей матрицы по указанным индексам и сохраняет его в файл.

    Параметры:
        index (tuple): Индексы элемента (строка, столбец) в результирующей матрице.
        matrix_a (list): Первая матрица.
        matrix_b (list): Вторая матрица.
        temp_file (str): Путь к временному файлу для записи промежуточных результатов.
    """
    row, col = index
    element_value = 0
    matrix_size = len(matrix_a[0])  # Размер строки в первой матрице (равен числу столбцов).

    # Вычисление значения элемента как суммы произведений элементов строки и столбца.
    for k in range(matrix_size):
        element_value += matrix_a[row][k] * matrix_b[k][col]

    # Сохранение результата в файл (добавление новой строки).
    with open(temp_file, 'a') as file:
        file.write(f"{row} {col} {element_value}\n")

    return row, col, element_value


def multiply_matrices(matrix_a, matrix_b, num_workers, temp_file):
    """
    Перемножает две матрицы с использованием многопоточности, записывая промежуточные результаты в файл.

    Параметры:
        matrix_a (list): Первая матрица.
        matrix_b (list): Вторая матрица.
        num_workers (int): Количество потоков для пула процессов.
        temp_file (str): Путь к временному файлу для записи промежуточных результатов.

    Возвращает:
        list: Результирующая матрица после умножения.
    """
    num_rows, num_cols = len(matrix_a), len(matrix_b[0])  # Размеры результирующей матрицы.
    task_indices = [(r, c) for r in range(num_rows) for c in range(num_cols)]  # Список задач (индексов элементов).

    # Удаляем временный файл, если он существует.
    if os.path.exists(temp_file):
        os.remove(temp_file)

    # Создаём пул процессов для параллельного выполнения.
    with multiprocessing.Pool(num_workers) as pool:
        # Параллельно вычисляем элементы матрицы.
        results = pool.starmap(
            calculate_element_and_save,
            [(index, matrix_a, matrix_b, temp_file) for index in task_indices]
        )

    # Создаём результирующую матрицу и заполняем её вычисленными значениями.
    result_matrix = [[0 for _ in range(num_cols)] for _ in range(num_rows)]
    for row, col, value in results:
        result_matrix[row][col] = value

    return result_matrix


def write_matrix_to_file(file_path, matrix):
    """
    Сохраняет матрицу в текстовый файл, каждая строка матрицы записывается в отдельную строку файла.

    Параметры:
        file_path (str): Путь к файлу для сохранения.
        matrix (list): Матрица для записи.
    """
    with open(file_path, 'w') as file:
        for row in matrix:
            file.write(' '.join(map(str, row)) + '\n')


def load_matrix_from_file(file_path):
    """
    Загружает матрицу из текстового файла, каждая строка файла превращается в строку матрицы.

    Параметры:
        file_path (str): Путь к файлу с матрицей.

    Возвращает:
        list: Матрица, считанная из файла.
    """
    with open(file_path, 'r') as file:
        return [list(map(int, line.split())) for line in file]


def create_random_matrix(size):
    """
    Создаёт случайную квадратную матрицу заданного размера с элементами от 0 до 10.

    Параметры:
        size (int): Размер матрицы (число строк и столбцов).

    Возвращает:
        list: Случайная квадратная матрица.
    """
    return [[random.randint(0, 10) for _ in range(size)] for _ in range(size)]


def async_matrix_tasks(matrix_size, stop_signal, output_folder):
    """
    Асинхронно генерирует случайные матрицы, умножает их и сохраняет результаты, пока не установлен сигнал остановки.

    Параметры:
        matrix_size (int): Размер генерируемых матриц.
        stop_signal (multiprocessing.Event): Сигнал остановки асинхронных операций.
        output_folder (str): Папка для сохранения файлов с матрицами и результатами.
    """
    iteration = 0
    temp_file = os.path.join(output_folder, "temp_results.txt")

    # Удаляем временный файл, если он существует.
    if os.path.exists(temp_file):
        os.remove(temp_file)

    while not stop_signal.is_set():  # Цикл продолжается, пока не установлен сигнал остановки.
        iteration += 1
        matrix_a = create_random_matrix(matrix_size)
        matrix_b = create_random_matrix(matrix_size)

        # Формируем пути для сохранения сгенерированных матриц.
        matrix_a_path = os.path.join(output_folder, f"matrix_a_iter{iteration}.txt")
        matrix_b_path = os.path.join(output_folder, f"matrix_b_iter{iteration}.txt")

        # Сохраняем сгенерированные матрицы в файлы.
        write_matrix_to_file(matrix_a_path, matrix_a)
        write_matrix_to_file(matrix_b_path, matrix_b)

        print(f"Итерация {iteration}: Матрицы сохранены в {matrix_a_path} и {matrix_b_path}.")

        # Умножаем матрицы и сохраняем результат.
        result_matrix = multiply_matrices(matrix_a, matrix_b, os.cpu_count(), temp_file)
        result_path = os.path.join(output_folder, f"result_matrix_iter{iteration}.txt")
        write_matrix_to_file(result_path, result_matrix)
        print(f"Итерация {iteration}: Результат сохранён в {result_path}.")


if __name__ == "__main__":
    # Размер матрицы.
    matrix_size = 5
    # Папка для хранения файлов.
    output_folder = "matrix_data"

    # Создаём папку, если её нет.
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Генерируем и сохраняем матрицы.
    matrix_a = create_random_matrix(matrix_size)
    matrix_b = create_random_matrix(matrix_size)
    matrix_a_file = os.path.join(output_folder, 'matrix_a.txt')
    matrix_b_file = os.path.join(output_folder, 'matrix_b.txt')
    write_matrix_to_file(matrix_a_file, matrix_a)
    write_matrix_to_file(matrix_b_file, matrix_b)

    print(f"Сгенерированы матрицы и сохранены в {matrix_a_file} и {matrix_b_file}.")

    # Проверяем возможность умножения матриц.
    if len(matrix_a[0]) != len(matrix_b):
        raise ValueError("Число столбцов первой матрицы не равно числу строк второй матрицы.")

    # Умножаем матрицы.
    temp_file = os.path.join(output_folder, "temp_results.txt")
    result_matrix = multiply_matrices(matrix_a, matrix_b, os.cpu_count(), temp_file)
    result_file = os.path.join(output_folder, 'result_matrix.txt')
    write_matrix_to_file(result_file, result_matrix)

    print(f"Результирующая матрица сохранена в {result_file}. Промежуточные результаты записаны в {temp_file}.")

    # Асинхронное выполнение.
    stop_signal = multiprocessing.Event()
    async_process = multiprocessing.Process(
        target=async_matrix_tasks,
        args=(matrix_size, stop_signal, output_folder)
    )

    async_process.start()
    time.sleep(10)  # Даем процессу поработать 10 секунд.
    stop_signal.set()  # Устанавливаем сигнал остановки.
    async_process.join()
    print("Асинхронные операции завершены.")
