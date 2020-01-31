#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import random
from PySide2.QtCore import Slot

from PySide2.QtWidgets import (QApplication, QHeaderView, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget, QFileDialog)


class Sequence:

    def __init__(self, machine1, machine2):
        self.machine1 = machine1
        self.machine2 = machine2

    """Metoda Johnosna"""

    def calculate(self):
        machine1=self.machine1[:]
        machine2=self.machine2[:]
        order = [0] * (len(machine1))
        left = 0
        right = -1
        for i in range(len(machine1)):
            if min(machine1) < min(machine2):
                index = machine1.index(min(machine1))  #najmniejszy element jest w tablicy 1
                # wypełnienie tablicy od strony lewej
                order[left] = index + 1
                left += 1
            else:
                # wypełnienie tablicy od strony prawej
                index = machine2.index(min(machine2))  #najmniejszy element jest w tablicy 2
                order[right] = index + 1
                right -= 1
            #Wypełnienie tablic dużymi liczbami aby nie można było ich wybrać w kolejnych iteracjach jako minimalne
            machine2[index] = max(machine1) + max(machine2)
            machine1[index] = max(machine1) + max(machine2)
        return order

    def get_time(self):
        order=self.calculate()
        time1 = 0
        time2 = self.machine1[order[0] - 1]
        for i in order:
            time1 +=self.machine1[i - 1]
            if time1 > time2:
                time2 += time1 - time2
            time2 +=  self.machine2[i - 1]
        return time2


class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Algorytm Johnsona")

        """Inicjlizacja zmiennych, na których będą dokynowane obliczenia oraz utworzenie obiektów
        (tabela,pola edycyjne,przyciski)"""

        self.j1 = []
        self.j2 = []
        self.W = 0

        self.jobs1 = QLineEdit()
        self.jobs2 = QLineEdit()
        self.tasks_count = QLineEdit()
        self.tasks_table = QTableWidget()

        self.file_name = QLineEdit()
        self.from_keys = QPushButton("Wprowadź dane")
        self.random = QPushButton("Generuj losowe wartości")
        self.from_file = QPushButton("Wprowadź dane z pliku")
        self.clear = QPushButton("Wyczyść")
        self.quit = QPushButton("Zamknij")
        self.solve = QPushButton("Rozwiąż")

        self.save = QPushButton("Zapis macierz do pliku")

        self.result = QLabel()
        self.time = QLabel()

        """Tworzenie layoutów a następnie dodawanie do nich widgetów"""

        self.left = QVBoxLayout()
        self.left.addWidget(QLabel("Ilość zadań"))
        self.left.addWidget(self.tasks_count)
        self.left.addWidget(self.from_keys)
        self.left.addWidget(self.random)
        self.left.addWidget(self.from_file)
        self.left.addWidget(self.clear)
        self.left.addWidget(self.quit)
        self.center = QVBoxLayout()
        self.right = QVBoxLayout()
        """Tworzenie  głównego layoutu a następnie dodawanie do nich trzech utworzonych wcześniej"""
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.left)
        self.layout.addLayout(self.center)
        self.layout.addLayout(self.right)

        self.setLayout(self.layout)

        """Komunikacja pomiędzy obiektami"""
        self.from_keys.clicked.connect(self.create_table)

        self.random.clicked.connect(self.create_table)
        self.random.clicked.connect(self.random_values)

        self.from_file.clicked.connect(self.create_table)
        self.from_file.clicked.connect(self.values_from_file)

        self.tasks_count.textChanged[str].connect(self.check_disable)

        self.solve.clicked.connect(self.solve_problem)
        self.clear.clicked.connect(self.clear_table)
        self.save.clicked.connect(self.save_to_file)
        self.quit.clicked.connect(self.quit_application)

    """Dodawanie do layoutu przycisków umożliwiających wybór metody obliczeń, zapisu do pliku oraz tekstu z wynikami"""

    def create_right_layout(self):

        self.layout.addLayout(self.right)
        self.right.addWidget(self.solve)

        self.right.addWidget(self.save)

        self.right.addWidget(self.result)
        self.right.addWidget(self.time)

        self.result.hide()  # wyniki ukryte dopóki użytkownik nie zażąda rozwiązania

    @Slot()
    def create_table(self):
        self.tasks_table.setColumnCount(int(self.tasks_count.text()))
        self.tasks_table.setRowCount(2)
        self.tasks_table.setVerticalHeaderLabels(["Maszyna 1.", "Maszyna 2."])

        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.center.addWidget(self.tasks_table)
        self.create_right_layout()

    @Slot()
    def random_values(self):

        for i in range(self.tasks_table.columnCount()):
            self.tasks_table.setItem(0, i, QTableWidgetItem(
                str(random.randint(1, 100))))
            self.tasks_table.setItem(1, i, QTableWidgetItem(
                str(random.randint(1, 100))))

    @Slot()
    def values_from_file(self):
        self.left.insertWidget(9, self.file_name)  # dodawanie widgetu,który będzie wyświetlał nazwę pliku
        self.file_name.setText(QFileDialog.getOpenFileName()[0])

        with open(self.file_name.text(), 'r') as f:
            for idx_line, line in enumerate(f):
                for idx, item in enumerate(line.split(' ')):
                    self.tasks_table.setItem(idx_line, idx, QTableWidgetItem(str(item)))

    """Zapisywanie tabeli do pliku"""

    @Slot()
    def save_to_file(self):

        self.file_name.setText(QFileDialog.getSaveFileName()[0])

        with open(self.file_name.text(), 'w') as f:
            for i in range(self.tasks_table.columnCount()):
                f.write(self.tasks_table.item(0, i).text() + ' ')
            f.write('\n')
            for j in range(self.tasks_table.columnCount()):
                f.write(self.tasks_table.item(1, j).text() + ' ')

    def convert_to_lists(self):

        for i in range(self.tasks_table.columnCount()):
            self.j1.append(int(self.tasks_table.item(0, i).text()))
        for j in range(self.tasks_table.columnCount()):
            self.j2.append(int(self.tasks_table.item(1, j).text()))

    @Slot()
    def solve_problem(self):
        self.convert_to_lists()
        best_sequence = Sequence(self.j1, self.j2)
        best = best_sequence.calculate()
        str_best = [str(i) for i in best]
        self.result.setText("Kolejność: " + " ".join(str_best))
        self.time.setText("Czas: " + str(best_sequence.get_time()))
        self.result.show()
        self.time.show()

    @Slot()
    def check_disable(self):
        actions = [self.from_keys, self.random, self.from_file]
        for action in actions:
            if not self.tasks_count.text():
                action.setEnabled(False)
            else:
                action.setEnabled(True)

    def clear_result(self):
        self.W = 0
        self.x = []
        self.y = []

    @Slot()
    def clear_table(self):
        self.tasks_table.setColumnCount(0)
        self.tasks_table.setRowCount(2)
        self.j1 = []
        self.j2 = []

    @Slot()
    def quit_application(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.resize(1000, 200)
    widget.show()
    sys.exit(app.exec_())
