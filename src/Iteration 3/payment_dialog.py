
from ui import smith_ui, login_ui, payment_ui
from Classes import employee, product, receipt, customer, reservation

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QSplashScreen, QProgressBar, QDialog, QMessageBox
import sys
from decimal import Decimal, ROUND_HALF_UP
import caution_dialog

import tkinter, tkinter.filedialog
import dataset
import datetime
import time
import ast
import table_model_class

import os
import xlrd

from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

class PaymentDialog(QtWidgets.QDialog, payment_ui.Ui_payment_dialog):
    """"""
    def __init__(self, parent, current_customer):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.main_window = parent
        self.current_customer = current_customer
        self.error_lbl.setText("")
        self.cash_rb.setChecked(True)
        self.total_lbl.setText(self.main_window.bc_total_lbl.text())
        self.setWindowTitle("Payment Dialog")
        self.toggle_text(True)

        self.set_customer_info()


        # Connections
        self.print_btn.clicked.connect(self.handle_print_btn)
        self.new_customer_cb.toggled.connect(self.toggle_new_customer)
        self.load_customer_info_btn.clicked.connect(self.get_customer)
        self.points_rb.toggled.connect(self.toggle_transaction_lbl)

    def set_customer_info(self):
        """"""
        if self.current_customer is not None:
            self.set_text(self.current_customer.customer_name, self.current_customer.customer_id, self.current_customer.customer_balance)
            self.toggle_text(False)
            self.customer_search_frame.setHidden(True)
            self.pay_with_points_lbl.setHidden(False)
            if self.can_customer_pay_with_points(): # customer has enough points to purchase
                self.points_rb.setEnabled(True)
                self.pay_with_points_lbl.setText("")
        else:
            self.points_rb.setEnabled(False)
            self.pay_with_points_lbl.setHidden(True)
            self.toggle_text(True)

    def handle_print_btn(self):
        """"""
        result = QMessageBox.question(self, 'Print Confirmation', "Are you certain you're ready to print?", QMessageBox.Yes, QMessageBox.No)
        # print("Result: {}".format(result))
        if result == QMessageBox.Yes:
            if self.current_customer is not None and not self.points_rb.isChecked():
                self.current_customer.customer_balance += self.points_to_earn
                self.customers_table = self.main_window.db['customers']
                self.customers_table.update(dict(id=self.current_customer.customer_id, point_balance=int(self.current_customer.customer_balance)), ['id'])

            if self.cash_rb.isChecked():
                self.main_window.print_("Cash")
            elif self.credit_rb.isChecked():
                self.main_window.print_("Credit Card")
            elif self.check_rb.isChecked():
                self.main_window.print_("Check")
            elif self.points_rb.isChecked():
                self.main_window.print_("Points")
                self.current_customer.customer_balance -= self.pay_with_points
                self.customers_table = self.main_window.db['customers']
                self.customers_table.update(dict(id=self.current_customer.customer_id, point_balance=int(self.current_customer.customer_balance)), ['id'])
            # print("Closing.")
            self.close()
        else:
            1+1

    def set_text(self, name, id, balance):
        """"""
        self.customer_name_lbl.setText(name)
        self.customer_id_lbl.setText(str(id))
        self.available_points_lbl.setText(str(balance))

    def toggle_text(self, bools):
        self.customer_frame.setHidden(bools)

    def get_customer(self): #
        """Get customer info from Database"""
        self.customers_table = self.main_window.db['customers']

        # Get a specific customer
        try:
            if not self.new_customer_cb.isChecked():
                try:
                    if not self.customer_name_field.text() == "":
                        if not self.customer_id_sbox.value() == 0:
                            try:
                                cust = self.customers_table.find_one(id=int(self.customer_id_sbox.value()), name=str(self.customer_name_field.text())) # TypeError: 'NoneType' object is not subscriptable
                            except Exception as e:
                                print(e)
                                # self.error = QMessageBox(icon=QMessageBox.Warning, text="There are no customers with those credentials in our database.")
                                # self.error.exec_()
                        else:
                            cust = self.customers_table.find_one(name=str(self.customer_name_field.text()))
                    else:
                        if not self.customer_id_sbox.value() == 0:
                            cust = self.customers_table.find_one(id=int(self.customer_id_sbox.value()))
                        else:
                            cust = None
                    try:
                        self.current_customer = customer.Customer(cust['id'], cust['name'], cust['point_balance'], cust['is_active'], cust['receipts'], cust['reservations'])  # id, name, pointBalance, activityStatus, receipts, reservations

                        self.set_text(self.current_customer.customer_name, self.current_customer.customer_id, self.current_customer.customer_balance)
                        self.set_customer_info()
                    except Exception as e:
                        print(e)
                        self.error = QMessageBox(icon=QMessageBox.Warning, text="There are no customers with those credentials in our database.")
                        self.error.exec_()
                except Exception as e:
                    print(e)
                    # TODO:
            else:
                try:
                    cust = self.customers_table.find_one(name=str(self.customer_name_field.text()))  # TypeError: 'NoneType' object is not subscriptable # TODO: check if the customer exists
                    self.current_customer = customer.Customer(cust['id'], cust['name'], cust['point_balance'], cust['is_active'], cust['receipts'],
                                                              cust['reservations'])  # id, name, pointBalance, activityStatus, receipts, reservations

                    self.set_text(self.current_customer.customer_name, self.current_customer.customer_id, self.current_customer.customer_balance)
                    self.set_customer_info()
                    self.error = QMessageBox(icon=QMessageBox.Warning, text="Customer already exists")
                    self.error.exec_()
                except Exception as e:
                    try:
                        self.customers_table.insert(dict(id=int(len(self.customers_table) + 1), name=self.customer_name_field.text(),
                                                         point_balance=0, is_active=True, receipts=None, reservations=None))  # ValueError: invalid literal for int() with base 10: ''
                        self.mc_new_customer_b = False
                        self.main_window.set_status_style("green")
                        self.main_window.statusbar.showMessage("***" + str(len(self.customers_table)) + ' ' + self.customer_name_field.text() + " added to Customer Database***", 4000)
                        self.current_customer = customer.Customer(len(self.customers_table), self.customer_name_field.text(), 0)
                        self.set_customer_info()
                    except ValueError as e:
                        print(e + " Error adding new customer")
                        self.main_window.set_status_style("red")
                        self.main_window.statusbar.showMessage("***Error--" + self.mc_id_lbl.text() + ' ' + self.mc_name_field.text() + " not added to Customer Database***", 4000)

        except TypeError:
            self.set_status_style("red")
            self.statusbar.showMessage("***Error--Customer does not exist. Invalid Name or ID***", 4000)

    def toggle_new_customer(self):
        """"""
        if self.new_customer_cb.isChecked():
            self.load_customer_info_btn.setText("Add New Customer")
            self.id_lbl.setHidden(True)
            self.customer_id_sbox.setHidden(True)
        else:
            self.load_customer_info_btn.setText("Load Customer Info")
            self.id_lbl.setHidden(False)
            self.customer_id_sbox.setHidden(False)

    def can_customer_pay_with_points(self):
        """"""
        self.points_table = self.main_window.db['points']
        self.spend_amount = self.points_table.find_one(id=0)
        self.pay_with_points = round(int(self.spend_amount['spend']) * self.main_window.total, 0)
        self.points_to_earn = round(self.main_window.total * int(self.spend_amount['earn']), 0)

        if self.current_customer.customer_balance >= self.pay_with_points:
            self.points_rb.setEnabled(True)
            if self.points_rb.isChecked():
                self.points_transaction_lbl.setText("This transaction will cost {} points".format(self.pay_with_points))
            else:
                self.points_transaction_lbl.setText("This transaction will earn {} points".format(self.points_to_earn))
            return True
        else:
            self.pay_with_points_lbl.setText("Not enough points ({})".format(self.pay_with_points))
            self.points_transaction_lbl.setText("This transaction will earn {} points".format(self.points_to_earn))
            self.points_rb.setEnabled(False)
            return False

    def toggle_transaction_lbl(self):
        if self.points_rb.isChecked():
            self.points_transaction_lbl.setText("This transaction will cost {} points".format(self.pay_with_points))
            self.pay_with_points_lbl.setStyleSheet("QLabel{color: green;}")
            self.pay_with_points_lbl.setText("Points available after transaction: {}".format(self.current_customer.customer_balance - self.pay_with_points))
        else:
            self.points_transaction_lbl.setText("This transaction will earn {} points".format(self.points_to_earn))
            self.pay_with_points_lbl.setText("")