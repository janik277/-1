import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        # Данные расходов
        self.expenses = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        # Поле суммы
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        # Поле категории
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_combo = ttk.Combobox(
            input_frame,
            values=["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        )
        self.category_combo.grid(row=0, column=3, padx=5)

        # Поле даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления расхода
        add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_button.grid(row=0, column=6, padx=5)

        # Таблица для отображения расходов
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Фрейм для фильтрации и подсчёта
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Фильтрация по категории
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, padx=5)
        self.filter_category = ttk.Combobox(
            filter_frame,
            values=["Все"] + ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        )
        self.filter_category.set("Все")
        self.filter_category.grid(row=0, column=1, padx=5)

        # Фильтрация по дате
        ttk.Label(filter_frame, text="С даты (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.start_date_entry = ttk.Entry(filter_frame)
        self.start_date_entry.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По дату (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5)
        self.end_date_entry = ttk.Entry(filter_frame)
        self.end_date_entry.grid(row=0, column=5, padx=5)

        # Кнопки фильтрации и подсчёта
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=6, padx=5)

        total_button = ttk.Button(filter_frame, text="Подсчитать сумму за период", command=self.calculate_total)
        total_button.grid(row=0, column=7, padx=5)

        # Метка для отображения общей суммы
        self.total_label = ttk.Label(self.root, text="Общая сумма: 0 руб.")
        self.total_label.pack(pady=5)

        self.refresh_table()

    def validate_input(self, amount_str, date_str):
        """Проверка корректности ввода"""
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат суммы")
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
            return False

        return True

    def add_expense(self):
        """Добавление нового расхода"""
        amount_str = self.amount_entry.get()
        category = self.category_combo.get()
        date_str = self.date_entry.get()

        if not all([amount_str, category, date_str]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        if not self.validate_input(amount_str, date_str):
            return

        expense = {
            "id": len(self.expenses) + 1,
            "amount": float(amount_str),
            "category": category,
            "date": date_str
        }

        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        self.clear_input()

    def clear_input(self):
        """Очистка полей ввода"""
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.date_entry.delete(0, tk.END)

    def refresh_table(self):
        """Обновление таблицы с расходами"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for expense in self.expenses:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f} руб.",
                expense["category"],
                expense["date"]
            ))

    def apply_filter(self):
        """Применение фильтров"""
        filtered = self.expenses

        # Фильтр по категории
        category_filter = self.filter_category.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]

        # Фильтр по дате
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
                return

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
                return

        # Обновление таблицы с отфильтрованными данными
        for item in self.tree.get_children():
            self.tree.delete(item)

        for expense in filtered:
            self.tree.insert("", "end", values=(
expense["id"],
                f"{expense['amount']:.2f} руб.",
                expense["category"],
                expense["date"]
            ))

    def calculate_total(self):
        """Подсчёт суммы расходов за выбранный период"""
        total = 0.0
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        # Если даты не указаны, считаем все расходы
        if not start_date_str and not end_date_str:
            total = sum(expense["amount"] for expense in self.expenses)
        else:
            filtered_expenses = self.expenses

            # Фильтр по начальной дате
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    filtered_expenses = [e for e in filtered_expenses
                                       if datetime.strptime(e["date"], "%Y-%m-%d") >= start_date]
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный формат начальной даты")
                    return

            # Фильтр по конечной дате
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    filtered_expenses = [e for e in filtered_expenses
                               if datetime.strptime(e["date"], "%Y-%m-%d") <= end_date]
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный формат конечной даты")
            total = sum(expense["amount"] for expense in filtered_expenses)

        self.total_label.config(text=f"Общая сумма: {total:.2f} руб.")

    def save_data(self):
        """Сохранение данных в JSON-файл"""
        try:
            with open("expenses.json", "w", encoding="utf-8") as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
        """Загрузка данных из JSON-файла"""
        if os.path.exists("expenses.json"):
            try:
                with open("expenses.json", "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                self.expenses = []
        else:
            self.expenses = []

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
