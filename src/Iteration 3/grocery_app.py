from ui import smith_ui, login_ui, payment_ui
from Classes import employee, product, receipt, customer, reservation

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QSplashScreen, QProgressBar, QDialog, QMessageBox
import sys
from decimal import Decimal, ROUND_HALF_UP
import caution_dialog, payment_dialog

import tkinter, tkinter.filedialog
import dataset
import datetime
import time
import ast
import table_model_class

import os
import xlrd

from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog
import winsound         # for sound
import time             # for sleep

# Get exception codes
# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    file = open("errorlog.txt", "a")
    print(exctype, value, traceback)
    file.write("\n\n", datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S "), exctype, value, traceback)
    file.close()
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class LoginDialog(QtWidgets.QDialog, login_ui.Ui_login_dialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent, Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.main_window = parent
        self.error_lbl.setText("")
        self.employee_id_field.setFocus()

        # connections
        self.sign_in_btn.clicked.connect(self.handle_sign_in_btn)
        self.employee_id_field.textChanged.connect(self.clear_error_lbl)
        self.password_field.textChanged.connect(self.clear_error_lbl)

    def handle_sign_in_btn(self):
        for employee in self.main_window.employee_list:
            if self.employee_id_field.text() == str(employee.employee_id) and self.password_field.text() == str(
                    employee.employee_password):
                self.main_window.employee_id_lbl.setText(str(employee.employee_id))
                self.main_window.employee_name_lbl.setText(employee.employee_name)
                self.main_window.current_employee = employee
                self.main_window.display_tabs()
                self.close()
            else:
                self.error_lbl.setText("Incorrect ID or Password")

    def clear_error_lbl(self):
        self.error_lbl.setText("")


class MainWindow(QMainWindow, smith_ui.Ui_main_window):
    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setupUi(self)

        # Setup
        self.setWindowTitle("Smith's Grocery")
        self.setWindowIcon(QtGui.QIcon('Assets/48x48.png'))
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        self.double_validator = QtGui.QDoubleValidator()
        self.int_validator = QtGui.QIntValidator()

        self.setWindowIcon(QtGui.QIcon('Assets/SmithsLogo.png'))
        self.cents = Decimal('.01')

        self.GREEN_STATUS = """QStatusBar {color: #008e14}"""

        self.RED_STATUS = """QStatusBar {color: red}"""

        # connecting to a SQLite database
        # self.db = dataset.connect('sqlite:///smith.db')
        self.db = dataset.connect('sqlite:///SmithsWebApp/smiths/smith.db')
        print("Connected " + str(self.db))
        self.employees_table = self.db['employees']
        self.points_table = self.db['points']
        # Insert admin record
        try:
            self.employees_table.insert(dict(id=0, name="admin", password="system", role=0))
        except:
            print("Database Exists")
            # winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            # time.sleep(0.25)  # in seconds (0.25 is 250ms)
            #
            # winsound.Beep(600, 250)
            # time.sleep(0.25)


        # Insert points rules
        try:
            self.points_table.insert(dict(id=0, earn=1, spend=100))
        except:
            print("Points Table Exists")

        try:
            self.products_table = self.db.create_table("products", primary_id='barcode', primary_type='Integer')
        except:
            print("Products Table Exists")
        self.get_employees()  # populate employee list
        self.current_employee = None
        self.launch_login_dialog()

        # Connections
        self.log_out_btn.clicked.connect(self.launch_login_dialog)

        #########################################
        # Manage Employee Initializing
        #########################################
        self.me_new_employee_b = False

        # Connections
        self.me_create_new_employee_btn.clicked.connect(self.handle_create_new_employee)
        self.me_delete_employee_btn.clicked.connect(self.handle_delete_employee)
        self.me_update_employee_btn.clicked.connect(self.handle_update_employee)
        self.me_employee_listview.clicked.connect(self.populate_employee_info)

        #########################################
        # Manage Product Initializing
        #########################################
        self.temporary_product_list = []
        self.temporary_product_list.append(product.Product("Apple", 1, 100, .25, 1.51, False, 0))
        self.temporary_product_list.append(product.Product("Orange", 2, 100, .35, 1.92, False, 0))
        self.mp_available_units_2_sbox.setHidden(True)
        self.white_space.setHidden(True)
        self.current_product = None
        self.mp_new_product_b = False
        self.mp_barcode_search_field.setValidator(self.int_validator)
        # self.mp_barcode_search_field.setValidator(self.int_validator)
        # self.mp_barcode_field.setValidator(self.int_validator)
        # self.mp_available_units_field.setValidator(self.double_validator)
        # self.mp_price_field.setValidator(self.double_validator)
        # self.mp_customer_price_field.setValidator(self.double_validator)
        # self.mp_provider_field.setValidator(self.int_validator)

        # Connections
        self.mp_barcode_search_field.returnPressed.connect(self.get_product)
        self.mp_search_btn.clicked.connect(self.get_product)
        self.mp_add_btn.clicked.connect(self.handle_add_new_product)
        self.mp_delete_btn.clicked.connect(self.handle_delete_product)
        self.mp_update_btn.clicked.connect(self.handle_update_product)
        self.mp_import_btn.clicked.connect(self.handle_import_spreadsheet)
        self.mp_weight_rb.toggled.connect(self.toggle_tens)

        ######################################### TODO
        # Manage Customers Initializing # TODO
        ######################################### TODO
        # self.customers_table = self.db['customers'] # TODO
        self.current_customer = None
        self.mc_new_customer_b = False

        for row in self.db['points']:
            self.earn_sbox.setValue(row['earn'])
            self.spend_sbox.setValue(row['spend'])

        # Connections
        self.mc_search_btn.clicked.connect(self.get_customer)
        self.mc_add_btn.clicked.connect(self.handle_add_new_customer)
        self.mc_update_btn.clicked.connect(self.handle_update_customer)
        self.mc_update_rules_btn.clicked.connect(self.handle_update_rules)

        #########################################
        # Manage Order Initializing
        #########################################
        self.receipts_table = self.db['receipts']
        self.initialize_manage_orders_tab()
        self.populate_mo_listview()

        # Connections
        self.mo_date_edit.dateChanged.connect(self.populate_mo_listview)
        self.mo_receipt_date_listview.clicked.connect(self.load_receipt)
        self.mo_receipt_listview.clicked.connect(self.enable_mo_remove_btn)
        self.mo_return_btn.clicked.connect(self.mo_handle_remove_item)
        self.mo_search_btn.clicked.connect(self.load_receipt_from_search)

        #########################################
        # Report Initializing
        #########################################
        self.initialize_reports_tab()

        # Connections
        self.r_date_edit_start.dateChanged.connect(self.r_date_changed)
        self.r_date_edit_end.dateChanged.connect(self.r_date_changed)
        self.r_print_btn.clicked.connect(self.handle_print_btn)

        #########################################
        # Reservations Initializing
        #########################################
        self.reservations_table = self.db['reservations']
        try:
            date = str(datetime.datetime.now().strftime("%m/%d/%Y"))
            self.reservations_table.insert(dict(id=0, customer_id=1, r_date=date, barcodes=str(['1','2','3']), quantities=str(['1', '2' , '3.22'])))
        except:
            print("Reservations Table Exists")
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
        #     print("Reservations table exists")

        #########################################
        # Begin Checkout Initializing
        #########################################
        self.reset_checkout()
        self.receipt_names = []
        self.receipt_text = []
        self.receipt_quantity = []
        self.receipt_price = []
        self.receipt_other = []
        self.tax_rate = Decimal(.047)
        self.subtotal = Decimal(0.0)
        self.tax = Decimal(0.0)
        self.total = Decimal(0.0)
        self.bc_barcode_search_field.setValidator(self.int_validator)
        self.bc_begin_checkout_btn.setFocus()
        self.bc_current_customer = None

        # Connections
        self.bc_begin_checkout_btn.clicked.connect(self.begin_checkout)
        self.bc_search_btn.clicked.connect(self.bc_get_product)
        self.bc_barcode_search_field.returnPressed.connect(self.bc_get_product)
        self.bc_quantity_sbox.valueChanged.connect(self.calculate_item_subtotal)
        self.bc_weight_sbox.valueChanged.connect(self.calculate_item_subtotal)
        self.bc_add_btn.clicked.connect(self.handle_add_item)
        self.bc_remove_btn.clicked.connect(self.handle_remove_item)
        self.bc_get_payment_btn.clicked.connect(self.launch_payment_dialog)
        self.bc_receipt_listview.clicked.connect(self.enable_remove_btn)
        self.bc_cancel_btn.clicked.connect(self.cancel_transaction)
        self.bc_load_reservation_btn.clicked.connect(self.handle_load_reservation_btn)
        # self.bc_weight_sbox.returnPressed.connect(self.handle_add_item)

##############################################################################################################################################################################################
#   Functions
##############################################################################################################################################################################################

    def launch_login_dialog(self):
        self.tabWidget.clear()
        self.employee_id_lbl.setText("")
        self.employee_name_lbl.setText("")
        self.login_dialog = LoginDialog(self)
        self.login_dialog.exec_()

    def get_employees(self):
        """Get employee list from database and read it into self.employee_list"""
        self.employee_list = []
        try:
            employees = self.db['employees'].all()
            # loop through what we get back from DB
            for emp in self.db['employees']:
                self.employee_list.append(
                    employee.Employee(int(emp['id']), str(emp['name']), str(emp['password']), int(emp['role'])))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Error loading employee data***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)


    def display_tabs(self):
        """Displays tabs based on user role. Admins have access to Manage Employees/Manage Products/Begin Checkout
        Cashiers only have access to Begin Checkout"""
        self.tabWidget.clear()

        if self.current_employee.role == 0:
            self.tabWidget.insertTab(0, self.begin_checkout_tab, "Begin Checkout")
            self.tabWidget.insertTab(0, self.reports_tab, "Reports")
            self.tabWidget.insertTab(0, self.manage_orders_tab, "Manage Orders")
            self.tabWidget.insertTab(0, self.manage_customers_tab, "Manage Customers")
            self.tabWidget.insertTab(0, self.manage_products_tab, "Manage Products")
            self.tabWidget.insertTab(0, self.manage_employees_tab, "Manage Employees")

            self.populate_me_employee_list_view()
            self.tabWidget.setCurrentIndex(0)
        elif self.current_employee.role == 1:
            self.tabWidget.insertTab(0, self.begin_checkout_tab, "Begin Checkout")
            self.tabWidget.insertTab(0, self.manage_orders_tab, "Manage Orders")
            self.tabWidget.setCurrentIndex(1)

    def set_status_style(self, color="green"):
        if color == "green":
            self.statusbar.setStyleSheet(self.GREEN_STATUS)
        else:
            self.statusbar.setStyleSheet(self.RED_STATUS)

    #########################################
    # Manage Employee Functions
    #########################################
    def populate_me_employee_list_view(self):
        """Read employee list into Manage Employees List View"""
        self.me_employee_list_model = QStandardItemModel(self.me_employee_listview)

        for employee in self.employee_list:
            item = QStandardItem(str(employee.employee_id) + ' ' + employee.employee_name)
            self.me_employee_list_model.appendRow(item)

        self.me_employee_listview.setModel(self.me_employee_list_model)
        self.me_new_employee_b = False


    def handle_create_new_employee(self):
        """Creates a new employee in the database"""
        self.me_new_employee_b = True

        self.me_id_lbl.setText(str(self.employee_list[-1].employee_id + 1))
        self.me_name_field.setText("")
        self.me_password_field.setText("")
        self.me_employee_gbox.setEnabled(True)
        self.me_create_new_employee_btn.setEnabled(False)
        self.me_update_employee_btn.setText("Insert Employee")
        self.me_update_employee_btn.setEnabled(True)
        self.me_delete_employee_btn.setEnabled(True)

    def handle_update_employee(self):
        """Updates employee info"""
        if self.me_name_field.text() != "":
            if self.me_new_employee_b:
                # print("Calling DB")  # update new employee
                # get a reference to the table 'user'
                self.employees_table = self.db['employees']
                # Insert a new record
                try:
                    self.employees_table.insert(dict(id=int(self.me_id_lbl.text()), name=self.me_name_field.text(),
                                                     password=self.me_password_field.text(),
                                                     role=self.me_role_cbox.currentIndex()))
                    self.me_new_employee_b = False
                    self.set_status_style("green")
                    self.statusbar.showMessage( self.me_name_field.text() + " added to Users***", 4000)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.me_name_field.text() + " not added to Users***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.me_create_new_employee_btn.setEnabled(True)
                self.me_update_employee_btn.setEnabled(False)
                self.me_delete_employee_btn.setEnabled(False)
                self.me_update_employee_btn.setText("Update Employee")
                self.me_id_lbl.setText("")
                self.me_name_field.setText("")
                self.me_password_field.setText("")

            else:
                self.employees_table = self.db['employees']
                # Update a record
                try:
                    self.employees_table.update(dict(id=int(self.me_id_lbl.text()), name=self.me_name_field.text(),
                                                     password=self.me_password_field.text(),
                                                     role=self.me_role_cbox.currentIndex()), ['id'])
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.me_name_field.text() + "\'s information updated***", 4000)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.me_name_field.text() + "\'s information not updated***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.me_create_new_employee_btn.setEnabled(True)
                self.me_update_employee_btn.setEnabled(False)
                self.me_delete_employee_btn.setEnabled(False)
                self.me_update_employee_btn.setText("Update Employee")
                self.me_id_lbl.setText("")
                self.me_name_field.setText("")
                self.me_password_field.setText("")
                self.me_delete_employee_btn.setEnabled(False)

            self.get_employees()  # recreate employee list
            self.populate_me_employee_list_view()  # reload employee list view

    def handle_delete_employee(self):
        """Delete employee from database"""
        result = QMessageBox.question(self, 'Delete Employee Confirmation', "Are you certain you want to delete this employee?", QMessageBox.Yes, QMessageBox.No)
        if result == QMessageBox.Yes:
            self.employees_table = self.db['employees']
            if self.me_id_lbl.text() != '0':
                try:
                    # Delete a record
                    # self.caution_dialog = caution_dialog.CautionDialog(self)
                    # self.caution_dialog.exec_()
                    # if self.caution_dialog.delete_b:
                    self.employees_table.delete(id=int(self.me_id_lbl.text()))
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.me_name_field.text() + " deleted from Users***", 4000)

                    self.me_id_lbl.setText("")
                    self.me_name_field.setText("")
                    self.me_password_field.setText("")
                    self.me_employee_gbox.setEnabled(False)
                    self.me_delete_employee_btn.setEnabled(False)
                    self.get_employees()  # recreate employee list
                    self.populate_me_employee_list_view()  # reload employee list view
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.me_name_field.text() + " not deleted from Users***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.me_create_new_employee_btn.setEnabled(True)
                self.me_delete_employee_btn.setEnabled(False)

    def populate_employee_info(self):
        """Displays selected employee info"""
        self.me_update_employee_btn.setEnabled(True)
        self.me_employee_gbox.setEnabled(True)
        self.me_delete_employee_btn.setEnabled(True)
        self.me_update_employee_btn.setEnabled(True)
        self.me_update_employee_btn.setText("Update Employee")
        self.edit_employee = self.employee_list[self.me_employee_listview.selectedIndexes()[0].row()]
        self.me_id_lbl.setText(str(self.edit_employee.employee_id))
        self.me_name_field.setText(self.edit_employee.employee_name)
        self.me_password_field.setText(self.edit_employee.employee_password)
        self.me_role_cbox.setCurrentIndex(int(self.edit_employee.role))
        self.me_new_employee_b = False

    #########################################
    # Manage Product Functions
    #########################################
    def get_product(self):
        """Get product info from Database"""
        self.products_table = self.db['products']
        # Get a specific product
        try:
            prod = self.products_table.find_one(barcode=int(self.mp_barcode_search_field.text())) # TypeError: 'NoneType' object is not subscriptable
            self.mp_add_btn.setEnabled(True)
            self.mp_delete_btn.setEnabled(True)
            self.mp_update_btn.setEnabled(True)
            self.mp_current_product = product.Product(prod['name'], prod['barcode'], prod['available_units'], prod['price'], prod['customer_price'], prod['weigh_b'], prod['provider'])
            self.mp_product_gbox.setEnabled(True)
            self.mp_name_field.setText(self.mp_current_product.name)
            self.mp_barcode_sbox.setValue(int(self.mp_current_product.barcode))
            self.mp_barcode_sbox.setEnabled(False)
            self.mp_price_sbox.setValue(float(self.mp_current_product.price))
            self.mp_customer_price_sbox.setValue(float(self.mp_current_product.customer_price))
            if self.mp_current_product.weigh_b:
                self.mp_weight_rb.setChecked(True)
                self.toggle_tens(True)
                self.mp_available_units_sbox.setValue(int(str(self.mp_current_product.available)[:-3]))
                self.mp_available_units_2_sbox.setValue(int(float(str(self.mp_current_product.available)[-2:])) * .01)
            else:
                self.mp_quantity_rb.setChecked(True)
                self.mp_available_units_sbox.setValue(int(self.mp_current_product.available))
                self.toggle_tens(False)
            self.mp_provider_sbox.setValue(int(self.mp_current_product.provider))
            self.mp_barcode_search_field.setText("")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Error--Invalid Barcode***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        self.mp_update_btn.setText("Update Product")

    def handle_add_new_product(self):
        """Clears product fields so new info can be added"""
        self.mp_new_product_b = True
        self.mp_add_btn.setEnabled(False)
        self.mp_product_gbox.setEnabled(True)
        self.mp_import_btn.setEnabled(True)
        self.mp_delete_btn.setEnabled(True)
        self.mp_update_btn.setEnabled(True)
        self.mp_name_field.setText("")
        self.mp_barcode_sbox.setEnabled(True)
        self.mp_barcode_sbox.setValue(0)
        self.mp_available_units_sbox.setValue(0)
        if self.mp_weight_rb.isChecked():
            self.mp_available_units_2_sbox_setValue(0)
        self.mp_price_sbox.setValue(0)
        self.mp_customer_price_sbox.setValue(0)
        self.mp_quantity_rb.setChecked(True)
        self.mp_provider_sbox.setValue(0)
        self.mp_current_product = product.Product(self.mp_name_field.text(), self.mp_barcode_sbox.value(),
                                                  self.mp_available_units_sbox.value(),
                                                  self.mp_price_sbox.value(), self.mp_customer_price_sbox.value(),
                                                  self.mp_quantity_rb.isChecked(), self.mp_provider_sbox.value())
        self.mp_update_btn.setText("Insert New Product")

    def handle_update_product(self):
        """Updates product info"""
        if self.mp_name_field.text() != "":
            if self.mp_new_product_b:
                self.products_table = self.db['products']
                price = str(Decimal(self.mp_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                cust_price = str(Decimal(self.mp_customer_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                if self.mp_quantity_rb.isChecked():
                    weigh = 0
                    available = self.mp_available_units_sbox.value()
                else:
                    weigh = 1
                    available = str(self.mp_available_units_sbox.value()) + str(self.mp_available_units_2_sbox.value())[1:4]
                # Update a record
                try:
                    price = str(Decimal(self.mp_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                    cust_price = str(Decimal(self.mp_customer_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))

                    self.products_table.insert(dict(barcode=int(self.mp_barcode_sbox.value()), name=self.mp_name_field.text(), available_units=available, price=price,
                                               customer_price=cust_price, weigh_b=weigh, provider=self.mp_provider_sbox.value())) # ValueError: invalid literal for int() with base 10: ''
                    self.mp_new_product_b = False
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.mp_name_field.text() + " added to Products Database***", 4000)

                    self.mp_update_btn.setText("Update Product")
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print("Error adding new item")

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--bardcode already in use. " + self.mp_name_field.text() + " not added to Products Database***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.mp_add_btn.setEnabled(True)
            else:
                self.products_table = self.db['products']
                price = str(Decimal(self.mp_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                cust_price = str(Decimal(self.mp_customer_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                if self.mp_quantity_rb.isChecked():
                    weigh = 0
                    available = self.mp_available_units_sbox.value()
                else:
                    weigh = 1
                    available = str(self.mp_available_units_sbox.value()) + str(self.mp_available_units_2_sbox.value())[1:4]
                    if available[-2:] == '.0':
                        available += '0'
                    price = str(Decimal(self.mp_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                    cust_price = str(Decimal(self.mp_customer_price_sbox.value()).quantize(self.cents, ROUND_HALF_UP))
                    print("Price: {}".format(price))
                    print("CPrice: {}".format(cust_price))
                try:
                    self.products_table.update(dict(name=self.mp_name_field.text(), barcode=int(self.mp_barcode_sbox.value()), available_units=available, price=price,
                                                    customer_price=cust_price, weigh_b=weigh, provider=self.mp_provider_sbox.value()), ['barcode'])  # ValueError: invalid literal for int() with base 10: ''
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.mp_name_field.text() + " information updated***", 4000)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print("Error updating item")

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.mp_name_field.text() + "\'s information not updated***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                # except:
                #     self.set_status_style("red")
                #     self.statusbar.showMessage("***Error--Another product with that barcode already exists***", 4000)

        else:

            self.set_status_style("red")
            self.statusbar.showMessage("***Error--Incomplete Please fill out all the product information***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def handle_delete_product(self):
        """Delete product from database"""
        self.products_table = self.db['products']
        try:

            # Delete a record
            result = QMessageBox.question(self, 'Delete Product Confirmation', "Are you certain you want to delete this product?", QMessageBox.Yes, QMessageBox.No)
            if result == QMessageBox.Yes:
                self.products_table.delete(barcode=int(self.mp_barcode_sbox.value()))
                self.set_status_style("green")
                self.statusbar.showMessage("***" + self.mp_name_field.text() + " deleted from Product Database***", 4000)
                self.mp_add_btn.setEnabled(True)
                self.mp_name_field.setText("")
                self.mp_barcode_sbox.setEnabled(True)
                self.mp_barcode_sbox.setValue(0)
                self.mp_available_units_sbox_setValue(0)
                if self.mp_weight_rb.isChecked():
                    self.mp_available_units_2_sbox_setValue(0)
                    self.mp_quantity_rb.setChecked(True)
                self.mp_price_sbox_setValue(0)
                self.mp_customer_price_sbox_setValue(0)
                self.mp_quantity_rb.setChecked(True)
                self.mp_provider_sbox_setValue(0)
                self.mp_product_gbox.setEnabled(False)
                self.mp_delete_btn.setEnabled(False)
                self.mp_update_btn.setEnabled(False)
                self.mp_update_btn.setText("Update Product")
        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Error--" + self.mp_name_field.text() + " not deleted from Product Database***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)


    def toggle_tens(self, event):
        self.white_space.setHidden(not event)
        self.mp_available_units_2_sbox.setHidden(not event)
        if event:
            self.mp_available_units_sbox.setAlignment(Qt.AlignRight)
        else:
            self.mp_available_units_sbox.setAlignment(Qt.AlignLeft)

    def handle_import_spreadsheet(self):
        file_options = {}
        file_options['filetypes'] = ('Excel Spreadsheet', '.xls')
        spreadsheet_root = tkinter.Tk()
        spreadsheet_root.withdraw()
        file_name = tkinter.filedialog.askopenfilename()
        if file_name != "":
            mp_sheet = xlrd.open_workbook(file_name).sheet_by_index(0)
            self.products_table = self.db['products']
            for i in range(mp_sheet.nrows):
                input_name = mp_sheet.cell_value(i, 0)
                input_price = mp_sheet.cell_value(i, 1)
                input_consumer_price = mp_sheet.cell_value(i, 2)
                input_weight = mp_sheet.cell_value(i, 3)
                input_provider = mp_sheet.cell_value(i, 4)
                input_available_units = mp_sheet.cell_value(i, 5)
                if self.products_table.find_one(name=input_name):
                    self.products_table.update(dict(name=input_name,
                         available_units=input_available_units,
                         price=input_price, customer_price=input_consumer_price,
                         weigh_b=input_weight, provider=input_provider), ['barcode'])
                else:
                    self.products_table.insert(
                        dict(name=input_name,
                             available_units=input_available_units,
                            price=input_price, customer_price=input_consumer_price,
                            weigh_b=input_weight, provider=input_provider), ['barcode'])


    #########################################
    # Manage Customers Functions
    #########################################
    def get_customer(self): #
        """Get customer info from Database"""
        self.mc_add_btn.setEnabled(True)
        self.customers_table = self.db['customers']
        # Get a specific customer
        try:
            if self.mc_name_id_search_field.text().isdigit(): # if it's a number
                cust = self.customers_table.find_one(id=int(self.mc_name_id_search_field.text())) # TypeError: 'NoneType' object is not subscriptable
            else:
                cust = self.customers_table.find_one(name=str(self.mc_name_id_search_field.text()))  # TypeError: 'NoneType' object is not subscriptable
            if cust['point_balance'] is None:
                cu_id = cust['id']
                self.customers_table.update(dict(name=cust['name'], point_balance=0, is_active=1), ['name'])
                self.cust = self.customers_table.find_one(id=cu_id)
            self.mc_activity_cb.setEnabled(True)
            self.mc_update_btn.setEnabled(True)
            self.mc_current_customer = customer.Customer(cust['id'], cust['name'], cust['point_balance'], cust['is_active'], cust['receipts'], cust['reservations']) # id, name, pointBalance, activityStatus, receipts, reservations
            self.mc_customer_gbox.setEnabled(True)
            self.mc_name_field.setText(self.mc_current_customer.customer_name)
            self.mc_id_lbl.setText(str(self.mc_current_customer.customer_id))
            self.mc_point_balance_sbox.setValue(self.mc_current_customer.customer_balance)
            self.mc_activity_cb.setChecked(self.mc_current_customer.is_active)

            self.mc_name_id_search_field.setText("")
        except TypeError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Error--Customer does not exist. Invalid Name or ID***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def handle_add_new_customer(self):
        """Clears customer fields so new info can be added"""
        self.mc_new_customer_b = True
        self.mc_customer_gbox.setEnabled(True)
        self.mc_activity_cb.setEnabled(True)
        self.mc_update_btn.setEnabled(True)
        self.mc_name_field.setText("")
        self.mc_id_lbl.setText(str(len(self.db['customers']) + 1))
        self.mc_point_balance_sbox.setValue(0)
        self.mc_activity_cb.setChecked(True)
        self.mc_current_customer = customer.Customer(self.mc_name_field.text(), self.mc_id_lbl.text(), self.mc_point_balance_sbox.value(), True) # id, name, pointBalance, activityStatus, receipts, reservations
        self.mc_add_btn.setEnabled(False)

    def handle_update_customer(self):
        """Updates customer info"""
        if self.mc_name_field.text() != "":
            if self.mc_new_customer_b:
                self.customers_table = self.db['customers']
                # Update a record
                try:
                    self.customers_table.insert(dict(id=int(self.mc_id_lbl.text()), name=self.mc_name_field.text(),
                                                    point_balance=self.mc_point_balance_sbox.value(), is_active=self.mc_activity_cb.isChecked(), receipts=None, reservations=None)) # ValueError: invalid literal for int() with base 10: ''
                    self.mc_new_customer_b = False
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.mc_id_lbl.text() + ' ' + self.mc_name_field.text() + " added to Customer Database***", 4000)
                except ValueError as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print(e + " Error adding new customer")

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.mc_id_lbl.text() + ' ' + self.mc_name_field.text() + " not added to Customer Database***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                self.mc_add_btn.setEnabled(True)
            else:
                self.mc_add_btn.setEnabled(True)
                self.customers_table = self.db['customers']
                try:
                    self.customers_table.update(dict(id=int(self.mc_id_lbl.text()), name=self.mc_name_field.text(),
                                                    point_balance=self.mc_point_balance_sbox.value(), is_active=self.mc_activity_cb.isChecked()), ['id']) # ValueError: invalid literal for int() with base 10: ''
                    self.set_status_style("green")
                    self.statusbar.showMessage("***" + self.mc_id_lbl.text() + ' ' + self.mc_name_field.text() + " information updated***", 4000)
                except ValueError as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print(e + " Error updating customer")

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error--" + self.mc_id_lbl.text() + ' ' + self.mc_name_field.text() + "\'s information not updated***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    # def handle_inactivate_customer(self):
    #     """Delete customer from database"""
    #     # TODO: confirmation dialog
    #     self.customers_table = self.db['customers']
    #     try:
    #         self.customers_table.delete(barcode=int(self.mc_barcode_field.text()))
            # self.set_status_style("green")
    #         self.statusbar.showMessage("***" + self.mc_name_field.text() + " deleted from Customer Database***", 4000)
    #     except:
                #self.set_status_style("red")
    #         self.statusbar.showMessage("***Error--" + self.mc_name_field.text() + " not deleted from Customer Database***", 4000)
    #     self.mc_name_field.setText("")
    #     self.mc_barcode_field.setText("")
    #     self.mc_available_units_field.setText("")
    #     self.mc_price_field.setText("")
    #     self.mc_customer_price_field.setText("")
    #     self.mc_quantity_rb.setChecked(True)
    #     self.mc_provider_field.setText("")
    #     self.mc_customer_gbox.setEnabled(False)
    #     self.mc_activity_cb.setEnabled(False)
    #     self.mc_update_btn.setEnabled(False)

    def handle_update_rules(self):
        try:
            self.points_table.update(dict(id=0, earn=self.earn_sbox.value(), spend=self.spend_sbox.value()), ['id'])  # ValueError: invalid literal for int() with base 10: ''
            self.set_status_style("green")
            self.statusbar.showMessage("***Point Rules updated***", 4000)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
            print("Error updating point rules")

            self.set_status_style("red")
            self.statusbar.showMessage("***Error--Point Rules not updated***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)


    #########################################
    # Manage Orders Functions
    #########################################
    def initialize_manage_orders_tab(self):
        """comment"""
        self.mo_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.mo_date_lbl.setText(str(self.mo_date_edit.date().toString("MMMM dd, yyyy")))
        # print("Manage Order init")

    def populate_mo_listview(self):
        """comment"""
        self.receipt_list = []
        self.mo_date_lbl.setText(str(self.mo_date_edit.date().toString("MMMM dd, yyyy")))
        self.receipt_call = self.receipts_table.find(date=self.mo_date_edit.date().toString("M/dd/yyyy"))

        for rec in self.receipt_call:
            name = ast.literal_eval(rec['name'])
            price = ast.literal_eval(rec['price'])
            quantity = ast.literal_eval(rec['quantity'])
            text = ast.literal_eval(rec['text'])
            other = ast.literal_eval(rec['other'])

            self.receipt_list.append(receipt.Receipt(rec['date'], name, price, quantity, text, other))

        self.mo_receipt_date_list_model = QStandardItemModel(self.mo_receipt_date_listview)

        for receip in self.receipt_list:
            item = QStandardItem(receip.other[0] + '-----$' + str(receip.other[6]))
            self.mo_receipt_date_list_model.appendRow(item)

        self.mo_receipt_date_listview.setModel(self.mo_receipt_date_list_model)

    def load_receipt(self):
        """comment"""
        # self.current_receipt = None
        self.mo_receipt_frame.setEnabled(True)
        self.current_receipt = self.receipt_list[self.mo_receipt_date_listview.selectedIndexes()[0].row()]

        self.mo_r_id_lbl.setText(str(self.current_receipt.other[0]))
        self.mo_r_date_lbl.setText(str(self.current_receipt.other[1]))
        emply = self.employees_table.find_one(id=self.current_receipt.other[2])
        self.mo_r_cashier_lbl.setText(str(emply['name']))
        self.mo_r_method_lbl.setText(str(self.current_receipt.other[3]))

        # print(str(self.current_receipt.other))

        self.mo_subtotal = Decimal(self.current_receipt.other[4]).quantize(self.cents, ROUND_HALF_UP)
        self.mo_tax = Decimal(self.current_receipt.other[5]).quantize(self.cents, ROUND_HALF_UP)
        self.mo_total = Decimal(self.current_receipt.other[6]).quantize(self.cents, ROUND_HALF_UP)

        self.mo_r_subtotal_lbl.setText("$" + str(self.mo_subtotal))
        self.mo_tax_lbl.setText("$" + str(self.mo_tax))
        self.mo_total_lbl.setText("$" + str(self.mo_total))

        self.mo_receipt_list_model = QStandardItemModel(self.mo_receipt_listview)
        self.mo_receipt_list_model.clear()

        for i in range(0, len(self.current_receipt.names)):
            if isinstance(self.current_receipt.quantity[i], int):
                item = QStandardItem(self.current_receipt.text[i] + " (" + str(self.current_receipt.quantity[i]) + ")\n$" + str(Decimal(int(self.current_receipt.quantity[i]) * float(self.current_receipt.price[i])).quantize(self.cents, ROUND_HALF_UP)))
            else:
                item = QStandardItem(self.current_receipt.text[i] + " (" + str(self.current_receipt.quantity[i]) + " lbs)\n$" + str(Decimal(Decimal(self.current_receipt.quantity[i]) * Decimal(self.current_receipt.price[i])).quantize(self.cents, ROUND_HALF_UP)))
            self.mo_receipt_list_model.appendRow(item)

        self.mo_receipt_listview.setModel(self.mo_receipt_list_model)
        # TODO

    def load_receipt_from_search(self):
        """comment"""
        self.receipts_table = self.db['receipts']
        try:
            rpt = self.receipts_table.find_one(r_id=int(self.mo_id_search_field.text()))
            name = ast.literal_eval(rpt['name'])
            price = ast.literal_eval(rpt['price'])
            quantity = ast.literal_eval(rpt['quantity'])
            text = ast.literal_eval(rpt['text'])
            other = ast.literal_eval(rpt['other'])

            self.current_receipt = receipt.Receipt(rpt['date'], name, price, quantity, text, other)


            self.mo_receipt_frame.setEnabled(True)

            self.mo_r_id_lbl.setText(str(self.current_receipt.other[0]))
            self.mo_r_date_lbl.setText(str(self.current_receipt.other[1]))
            emply = self.employees_table.find_one(id=self.current_receipt.other[2])
            self.mo_r_cashier_lbl.setText(str(emply['name']))
            self.mo_r_method_lbl.setText(str(self.current_receipt.other[3]))

            # print(str(self.current_receipt.other))

            self.mo_subtotal = Decimal(self.current_receipt.other[4]).quantize(self.cents, ROUND_HALF_UP)
            self.mo_tax = Decimal(self.current_receipt.other[5]).quantize(self.cents, ROUND_HALF_UP)
            self.mo_total = Decimal(self.current_receipt.other[6]).quantize(self.cents, ROUND_HALF_UP)

            self.mo_r_subtotal_lbl.setText("$" + str(self.mo_subtotal))
            self.mo_tax_lbl.setText("$" + str(self.mo_tax))
            self.mo_total_lbl.setText("$" + str(self.mo_total))

            self.mo_receipt_list_model = QStandardItemModel(self.mo_receipt_listview)
            self.mo_receipt_list_model.clear()

            for i in range(0, len(self.current_receipt.names)):
                if isinstance(self.current_receipt.quantity[i], int):
                    item = QStandardItem(self.current_receipt.text[i] + " (" + str(self.current_receipt.quantity[i]) + ")\n$" + str(Decimal(int(self.current_receipt.quantity[i]) * float(self.current_receipt.price[i])).quantize(self.cents, ROUND_HALF_UP)))
                else:
                    item = QStandardItem(self.current_receipt.text[i] + " (" + str(self.current_receipt.quantity[i]) + " lbs)\n$" + str(Decimal(Decimal(self.current_receipt.quantity[i]) * Decimal(self.current_receipt.price[i])).quantize(self.cents, ROUND_HALF_UP)))
                self.mo_receipt_list_model.appendRow(item)

            self.mo_receipt_listview.setModel(self.mo_receipt_list_model)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Search Error--Please enter a valid Receipt ID***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def enable_mo_remove_btn(self):
        self.mo_btn_frame.setEnabled(True)

    def mo_handle_remove_item(self):
        """Removes selected item from listview and receipt lists"""
        try:
            row = self.mo_receipt_listview.selectedIndexes()[0].row()

            # print("row: " + str(row))
            # print("Quantity: {}\nPrice: {}".format(str(self.current_receipt.quantity[row]), str(self.current_receipt.price[row])))
            # UPDATE TOTALS
            if not isinstance(self.current_receipt.quantity[row], int):
                self.mo_subtotal -= Decimal(float(self.current_receipt.quantity[row]) * float(self.current_receipt.price[row])).quantize(self.cents, ROUND_HALF_UP)
                self.mo_tax -= Decimal((float(self.current_receipt.quantity[row]) * float(Decimal(float(self.current_receipt.price[row])) * self.tax_rate.quantize(self.cents, ROUND_HALF_UP)))).quantize(self.cents, ROUND_HALF_UP)
                self.mo_total -= \
                    Decimal(
                        float(self.current_receipt.quantity[row]) * float(self.current_receipt.price[row]))\
                        .quantize(self.cents, ROUND_HALF_UP) + Decimal(
                        (Decimal(self.current_receipt.quantity[row]) * Decimal(self.current_receipt.price[row])) * self.tax_rate).quantize(self.cents, ROUND_HALF_UP)
            else:
                self.mo_subtotal -= Decimal(int(self.current_receipt.quantity[row]) * Decimal(self.current_receipt.price[row]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)
                self.mo_tax -= Decimal((int(self.current_receipt.quantity[row]) * Decimal(self.current_receipt.price[row])) * self.tax_rate).quantize(self.cents, ROUND_HALF_UP)
                self.mo_total -= Decimal(int(self.current_receipt.quantity[row])
                                        * Decimal(self.current_receipt.price[row]).quantize(self.cents,ROUND_HALF_UP)).quantize(self.cents,ROUND_HALF_UP) \
                                        + Decimal((int(self.current_receipt.quantity[row])
                                        * Decimal(self.current_receipt.price[row]))
                                        * self.tax_rate).quantize(self.cents, ROUND_HALF_UP)

            # Update totals labels
            self.mo_r_subtotal_lbl.setText('$' + str(Decimal(self.mo_subtotal).quantize(self.cents, ROUND_HALF_UP)))
            self.mo_tax_lbl.setText('$' + str(Decimal(self.mo_tax).quantize(self.cents, ROUND_HALF_UP)))
            self.mo_total_lbl.setText('$' + str(Decimal(self.mo_total).quantize(self.cents, ROUND_HALF_UP)))

            self.current_receipt.other[4] = str(self.mo_subtotal)
            self.current_receipt.other[5] = str(self.mo_tax)
            self.current_receipt.other[6] = str(self.mo_total)

            self.mo_receipt_list_model.removeRow(row)

            self.mo_update_inventory(row)

            self.current_receipt.names.pop(row)
            self.current_receipt.text.pop(row)
            self.current_receipt.quantity.pop(row)
            self.current_receipt.price.pop(row)


            self.mo_update_receipt()
            self.populate_mo_listview()

        except IndexError as e:  # If no items are selected
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Index Error--Please select an item***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def mo_update_inventory(self, row):
        """"""
        try:
            self.products_table = self.db['products']
            # print("Successful connection to product db")
            prod = self.products_table.find_one(barcode=int(self.current_receipt.names[row]))
            # print("Successful prodcut barcode: " + str(prod['name']))
            if prod['weigh_b']:
                new_quantity = Decimal(prod['available_units']).quantize(self.cents, ROUND_HALF_UP) + Decimal(self.current_receipt.quantity[row]).quantize(self.cents, ROUND_HALF_UP)
            else:
                new_quantity = int(prod['available_units']) + self.current_receipt.quantity[row]
            self.products_table.update(dict(barcode=prod['barcode'], available_units=str(new_quantity)), ['barcode'])

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Error updating inventory***", 4000)
            print("Error updating inventory")
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def mo_update_receipt(self):
        """"""
        print("Updating receipt")
        self.receipts_table = self.db['receipts']
        self.receipts_table.update(dict(other=str(self.current_receipt.other), name=str(self.current_receipt.names), quantity=str(self.current_receipt.quantity), price=str(self.current_receipt.price), text=str(self.current_receipt.text), r_id=self.current_receipt.other[0]), ['r_id'])

    #########################################
    # Reports Functions
    #########################################
    def initialize_reports_tab(self):
        """comment"""
        self.r_date_edit_start.setDateTime(QtCore.QDateTime.currentDateTime())
        self.r_date_edit_end.setDateTime(QtCore.QDateTime.currentDateTime())

        # self.report_table.horizontalHeader().setDefaultAlignment(Qt.AlignRight)
        self.report_list = [["", "", ""]]
        self.header = ["Product", "Total Sold", "Revenue"]
        table_model = table_model_class.TableModel(self, self.report_list, self.header)
        self.report_table.setModel(table_model)
        self.model = self.report_table.model()

        start_date = int(time.mktime(self.r_date_edit_start.date().toPyDate().timetuple()))
        end_date = int(time.mktime(self.r_date_edit_end.date().toPyDate().timetuple())) + 86399

        self.report_db_call(start_date, end_date)

    def r_date_changed(self):
        """comment"""
        start_date = int(time.mktime(self.r_date_edit_start.date().toPyDate().timetuple()))
        end_date = int(time.mktime(self.r_date_edit_end.date().toPyDate().timetuple())) + 86399

        if start_date < end_date:
            self.r_beg_lbl.setText("Beginning Date")
            self.r_end_lbl.setText("Ending Date")
            self.report_db_call(start_date, end_date)
        else:
            start_date = int(time.mktime(self.r_date_edit_end.date().toPyDate().timetuple()))
            end_date = int(time.mktime(self.r_date_edit_start.date().toPyDate().timetuple())) + 86399
            self.r_beg_lbl.setText("Ending Date")
            self.r_end_lbl.setText("Beginning Date")
            self.report_db_call(start_date, end_date)

    def report_db_call(self, date_start, date_end):
        """comment"""
        self.rec_table = self.db['receipts'].all()

        self.report_receipt_list = []

        for rect in self.rec_table:
            # print("Receipt time: " + str(rect['date_time']))
            # print("Start time: " + str(date_start))
            # print("End time: " + str(date_end))
            # print("\n\n")
            if rect['date_time'] >= date_start and rect['date_time'] <= date_end:
                name = ast.literal_eval(rect['name'])
                price = ast.literal_eval(rect['price'])
                quantity = ast.literal_eval(rect['quantity'])
                text = ast.literal_eval(rect['text'])
                other = ast.literal_eval(rect['other'])

                self.report_receipt_list.append(receipt.Receipt(rect['date'], name, price, quantity, text, other))

        print("Report Receipt List: {}".format(self.report_receipt_list))
        self.calculate_totals()

    def calculate_totals(self):
        """comment"""
        # Create master list
        try:
            self.master_list = []
            self.total_orders = 0
            self.total_revenue = Decimal(0.00).quantize(self.cents, ROUND_HALF_UP)
            self.first_time_b = True

            for order in self.report_receipt_list:
                # Read through items on the receipt
                self.total_orders += 1
                for i in range(0, len(order.names)):
                    # Check if product is in master list
                    if self.first_time_b:
                        # print("This is the first and only time")
                        self.master_list.append(["", "", ""])
                        self.first_time_b = False
                    self.unique_b = True
                    for sublist in self.master_list:
                        if sublist[0] == order.text[i]: # item exists in master_list
                            #print("sublist[0]: {} \norder.text[i]: {}\n".format(sublist[0], order.text[i]))
                            print("It exists! I'm updating it.")
                            # add to total and revenue
                            print("sublist[1]: {} \norder.quantity[i]: {}\n".format(sublist[1], order.quantity[i]))
                            sublist[1] += order.quantity[i]
                            if isinstance(order.quantity[i], int):
                                sublist[2] += Decimal(int(order.quantity[i]) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP) # TODO
                                self.total_revenue += Decimal(int(order.quantity[i]) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)
                            else:
                                sublist[2] += Decimal(Decimal(order.quantity[i]).quantize(self.cents, ROUND_HALF_UP) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)
                                self.total_revenue += Decimal(Decimal(order.quantity[i]).quantize(self.cents, ROUND_HALF_UP) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)

                            self.unique_b = False
                    if self.unique_b: # The item hasn't been added to the master_list yet
                        # add a new list to the master_list
                        print("It doesn't exist! I'm adding it.")
                        if isinstance(order.quantity[i], int):
                            rev = Decimal(int(order.quantity[i]) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)
                            self.master_list.append([order.text[i], order.quantity[i], rev])
                            self.total_revenue += rev
                        else:
                            rev = Decimal(Decimal(order.quantity[i]).quantize(self.cents, ROUND_HALF_UP) * Decimal(order.price[i]).quantize(self.cents, ROUND_HALF_UP)).quantize(self.cents, ROUND_HALF_UP)
                            self.master_list.append([order.text[i], order.quantity[i], rev])
                            self.total_revenue += rev


            # self.master_list.append(["", "", "", "Total Orders", self.total_orders])
            # self.master_list.append(["", "", "", "Total Revenue", self.total_revenue])
            self.r_total_orders_lbl.setText(str(self.total_orders))
            self.r_total_revenue_lbl.setText('$' + str(self.total_revenue))
            # Keep running total of receipts and Total Revenue
            if len(self.master_list) > 0:
                self.master_list.pop(0)
            for subl in self.master_list:
                subl[2] = "$" + str(subl[2])
            # print(str(self.master_list))
            table_model = table_model_class.TableModel(self, self.master_list, self.header)
            self.report_table.setModel(table_model)
            self.model = self.report_table.model()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Report Error***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def handle_print_btn(self):
        """comment"""
        report = u""
        if not self.master_list == []:
            if self.r_alpha_rb.isChecked():
                self.master_list.sort(key=lambda row: row[0])
            elif self.r_total_rb.isChecked():
                self.master_list.sort(key=lambda row: row[1])
            elif self.r_revenue_rb.isChecked():
                for item in self.master_list:
                    item[2] = item[2].replace("$", "")
                self.master_list.sort(key=lambda row: float(row[2]))
                for item in self.master_list:
                    item[2] = '$' + str(item[2])

            if self.r_desc_rb.isChecked():
                self.master_list = self.master_list[::-1]

            if self.r_beg_lbl.text() == "Beginning Date":
                report += "Report " + self.r_date_edit_start.date().toString("MM/dd/yyyy") + ' - ' +  self.r_date_edit_end.date().toString("MM/dd/yyyy") + '\n\n'
            else:
                report += "Report " + self.r_date_edit_end.date().toString("MM/dd/yyyy") + ' - ' + self.r_date_edit_start.date().toString("MM/dd/yyyy") + '\n\n'
            # report += "{:>30} {:>30} {:>30}\n".format(str(self.header[0]), str(self.header[1]), str(self.header[2]))
            # report += "{:>34} {:>30} {:>33}\n".format("-----------", "-------------", "------------")
            for sublist in self.master_list:
                # report+=str(sublist[0]) + ((10 - len(str(sublist[0]))) * '*') + str(sublist[1]) + ((6 - len(str(sublist[1]))) * '*') + str(sublist[2]) +"\n"
                if isinstance(sublist[1], int):
                    report += "{}\n{}\n{}\n\n".format(str(sublist[0]), str(sublist[1]), str(sublist[2]))
                else:
                    report += "{}\n{} lbs\n{}\n\n".format(str(sublist[0]), str(sublist[1]), str(sublist[2]))
            report += "\nTotal Orders: " + str(self.total_orders) + "\nTotal Revenue: $" + str(self.total_revenue)
            # print(report)
            printer = QPrinter()
            doc = QTextDocument(report)
            dialog = QPrintDialog(printer)
            dialog.setModal(True)
            dialog.setWindowTitle("Print Report")

            # dialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)
            if dialog.exec_() == True:
                try:
                    doc.print_(printer)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print("?")
        else:

            self.set_status_style("red")
            self.statusbar.showMessage("***Empty report. Please select dates with at least one order.***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)


    #########################################
    # Begin Checkout Functions
    #########################################
    def begin_checkout(self):
        """Begin transaction and show checkout screen"""
        self.bc_begin_checkout_btn.setHidden(True)
        self.bc_checkout_frame.setHidden(False)
        self.bc_cancel_btn.setEnabled(True)
        self.bc_barcode_search_field.setFocus()
        self.co_product_list = []
        self.co_quantity = []

    def cancel_transaction(self):
        """Cancels transaction and sets checkouts to initialization"""
        self.bc_begin_checkout_btn.setHidden(False)
        self.bc_checkout_frame.setHidden(True)
        self.bc_cancel_btn.setEnabled(False)

        self.reset_checkout()
        self.receipt_names = []
        self.receipt_quantity = []
        self.receipt_price = []
        self.receipt_other = []
        self.receipt_text = []
        self.cents = Decimal('.01')
        self.tax_rate = Decimal(.047)
        self.subtotal = Decimal(0.0)
        self.tax = Decimal(0.0)
        self.total = Decimal(0.0)

        # reset listview
        self.bc_receipt_list_model = QStandardItemModel(self.bc_receipt_listview)
        self.bc_receipt_listview.setModel(self.bc_receipt_list_model)

        # Update totals labels
        self.bc_r_subtotal_lbl.setText('$' + str(self.subtotal) + ".00")
        self.bc_tax_lbl.setText('$' + str(self.tax) + ".00")
        self.bc_total_lbl.setText('$' + str(self.total) + ".00")

        self.bc_quantity_frame.setEnabled(False)
        self.current_product = None
        self.bc_item_info_frame.setEnabled(False)
        self.bc_name_lbl.setText("")
        self.bc_barcode_lbl.setText("")
        self.bc_available_lbl.setText("")
        self.bc_price_lbl.setText("")
        self.bc_weight_sbox.setEnabled(False)
        self.bc_quantity_sbox.setEnabled(False)
        self.bc_quantity_lbl.setEnabled(False)
        self.bc_weight_lbl.setEnabled(False)
        self.bc_provider_lbl.setText("")
        self.bc_subtotal_lbl.setText("")
        self.bc_barcode_search_field.setText("")
        self.bc_btn_frame.setEnabled(False)

        self.bc_current_customer = None

    def enable_remove_btn(self):
        self.bc_remove_btn.setEnabled(True)

    def reset_checkout(self):
        """Show checkout frame"""
        self.bc_checkout_frame.setHidden(True)

    def handle_load_reservation_btn(self):
        """"""
        if not self.bc_customer_name_field.text() == "":
            self.reservations_table = self.db['reservations']
            self.customers_table = self.db['customers']
            self.products_table = self.db['products']

            try:
                if self.bc_customer_name_field.text().isdigit():
                    try:
                        self.cust = self.customers_table.find_one(id=int(self.bc_customer_name_field.text()))
                        print("customer found! (id) {}".format(self.cust['id']))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                        print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                        self.set_status_style("red")
                        self.statusbar.showMessage("***Invalid Customer ID***", 4000)
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                else:
                    try:
                        self.cust = self.customers_table.find_one(name=self.bc_customer_name_field.text())
                        print("customer found! (name) {}".format(self.cust['id']))
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                        print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                        self.set_status_style("red")
                        self.statusbar.showMessage("***Invalid Customer Name***", 4000)
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                try:
                    if self.cust['point_balance'] is None:
                        cu_id = self.cust['id']
                        self.customers_table.update(dict(name=self.cust['name'], point_balance=0, is_active=1), ['name'])
                        self.cust = self.customers_table.find_one(id=cu_id)
                    self.res = self.reservations_table.find_one(id=int(self.bc_reservation_num_sbox.value()))
                    print("Customer ID: {}\nRes Customer ID: {}".format(self.cust['id'], self.res['customer_id']))
                    if self.cust['id'] == self.res['customer_id']:
                        barcodes = ast.literal_eval(self.res['barcodes'])
                        quantities = ast.literal_eval(self.res['quantities'])
                        # print("Barcodes: {}\nQuantities: {}".format(barcodes, quantities))
                        self.current_reservation = reservation.Reservation(self.res['id'], self.res['customer_id'], self.res['r_date'], barcodes, quantities)
                        # print("Customer ID:" + str(self.current_reservation.customer_id))

                        self.bc_current_customer = customer.Customer(self.cust['id'], self.cust['name'], self.cust['point_balance'], self.cust['is_active'], self.cust['receipts'], self.cust['reservations']) # id, name, pointBalance, activityStatus=True, receipts=None, reservations=None)
                        # print("Customer: " + str(self.bc_current_customer.customer_name))
    
                        self.load_reservation(self.current_reservation.barcodes, self.current_reservation.quantities)
                    else:

                        self.set_status_style("red")
                        self.statusbar.showMessage("***This Customer does not have a reservation by that number***", 4000)
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                    print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                    self.set_status_style("red")
                    self.statusbar.showMessage("***Error, no reservation found***", 4000)
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

                self.set_status_style("red")
                self.statusbar.showMessage("***Invalid Entry***", 4000)
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        else:
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Please Enter Customer Name***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def load_reservation(self, barcodes, quantities):
        self.barcodes = barcodes
        self.quantities = quantities

        for x in range(0, len(self.barcodes)):
            try:
                # print("Barcode: {}".format(self.barcodes[x]))
                result = self.products_table.find_one(barcode=int(self.barcodes[x]))
                # print("Get here?")
                # print("Result: {}".format(result['name']))
                self.res_current_product = product.Product(result['name'], result['barcode'], result['available_units'], result['price'], result['customer_price'], result['weigh_b'], result['provider'])  # product_name, product_barcode, product_available, product_price, customer_price, weigh, product_provider)
                self.res_quantity = self.quantities[x]
                # print("Current Product: {}".format(self.res_current_product))
                # print("0")
                self.res_handle_add_item()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

    def res_handle_add_item(self):
        """Add item to receipt and lists"""
        # Store barcode, quantity/weight, price for receipt storage
        self.receipt_names.append(str(self.res_current_product.barcode)) #TODO
        self.receipt_text.append(str(self.res_current_product.name))
        if '.' in self.res_quantity:
            self.res_quantity = float(self.res_quantity)
            print("We have a float! {}".format(self.res_quantity))
        else:
            self.res_quantity = int(self.res_quantity)
            print("We have an int! {}".format(self.res_quantity))
        self.receipt_quantity.append(self.res_quantity)  # CANNOT BE STRINGS.

        self.receipt_price.append(str(self.res_current_product.customer_price))
        self.res_update_receipt()

    def res_update_receipt(self):
        if not self.bc_receipt_frame.isEnabled():
            self.bc_receipt_list_model = QStandardItemModel(self.bc_receipt_listview)
        self.bc_receipt_frame.setEnabled(True)

        if self.res_current_product.weigh_b:
            item = QStandardItem(self.res_current_product.name + ' (' + str(Decimal(self.res_quantity).quantize(self.cents, ROUND_HALF_UP)) + ' lbs)\n$' + str(
                Decimal(Decimal(self.res_quantity) * Decimal(self.res_current_product.customer_price)).quantize(self.cents, ROUND_HALF_UP)))
        else:
            item = QStandardItem(self.res_current_product.name + ' (' + str(self.res_quantity) + ')\n$' + str(
                Decimal(int(self.res_quantity) * Decimal(self.res_current_product.customer_price)).quantize(self.cents, ROUND_HALF_UP)))

        self.bc_receipt_list_model.appendRow(item)
        self.bc_receipt_listview.setModel(self.bc_receipt_list_model)

        #Calculate totals
        self.subtotal += Decimal(Decimal(self.res_quantity).quantize(self.cents, ROUND_HALF_UP) * Decimal(self.res_current_product.customer_price)).quantize(self.cents, ROUND_HALF_UP)
        self.tax += Decimal((Decimal(self.res_quantity).quantize(self.cents, ROUND_HALF_UP) * Decimal(self.res_current_product.customer_price)) * self.tax_rate).quantize(self.cents, ROUND_HALF_UP)
        self.total = self.subtotal + self.tax

        # Update totals labels
        self.bc_r_subtotal_lbl.setText('$' + str(self.subtotal))
        self.bc_tax_lbl.setText('$' + str(self.tax))
        self.bc_total_lbl.setText('$' + str(self.total))

        self.bc_btn_frame.setEnabled(True)


    def bc_get_product(self):
        """Get product info from database and populate labels"""
        print("Calling DB - Product Lookup")
        self.products_table = self.db['products']
        # Get a specific product
        try:
            prod = self.products_table.find_one(barcode=int(self.bc_barcode_search_field.text()))

            self.current_product = product.Product(prod['name'], prod['barcode'], prod['available_units'], prod['price'],
                                                      prod['customer_price'], prod['weigh_b'], prod['provider'])
            self.bc_quantity_sbox.setValue(0)
            self.bc_weight_sbox.setValue(0.00)
            self.bc_quantity_frame.setEnabled(True)
            self.bc_item_info_frame.setEnabled(True)
            self.bc_name_lbl.setText(self.current_product.name)
            self.bc_barcode_lbl.setText(str(self.current_product.barcode))
            self.bc_available_lbl.setText(str(self.current_product.available))
            self.bc_price_lbl.setText(str(self.current_product.customer_price))
            if self.current_product.weigh_b:
                self.bc_weight_sbox.setEnabled(True)
                self.bc_quantity_sbox.setEnabled(False)
                self.bc_quantity_lbl.setEnabled(False)
                self.bc_weight_lbl.setEnabled(True)
            else:
                self.bc_weight_lbl.setEnabled(False)
                self.bc_weight_sbox.setEnabled(False)
                self.bc_quantity_sbox.setEnabled(True)
                self.bc_quantity_lbl.setEnabled(True)
            self.bc_provider_lbl.setText(str(self.current_product.provider))
            self.calculate_item_subtotal()
            self.bc_barcode_search_field.setText("")
            self.bc_btn_frame.setEnabled(True)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Invalid Barcode***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def calculate_item_subtotal(self):
        try:
            if self.current_product.weigh_b:
                self.bc_subtotal_lbl.setText(str(Decimal(Decimal(self.bc_weight_sbox.value()) * Decimal(self.current_product.customer_price)).quantize(self.cents, ROUND_HALF_UP)))
            else:
                self.bc_subtotal_lbl.setText(str(Decimal(Decimal(self.bc_quantity_sbox.value()) * Decimal(self.current_product.customer_price)).quantize(self.cents, ROUND_HALF_UP)))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

    def handle_add_item(self):
        """Add item to receipt and lists"""
        # Store barcode, quantity/weight, price for receipt storage
        self.receipt_names.append(self.bc_barcode_lbl.text())
        self.receipt_text.append(self.bc_name_lbl.text())
        if self.current_product.weigh_b:
            self.receipt_quantity.append(float(Decimal(self.bc_weight_sbox.value()).quantize(self.cents, ROUND_HALF_UP)))
        else:
            self.receipt_quantity.append(self.bc_quantity_sbox.value())
        self.receipt_price.append(self.bc_price_lbl.text())

        self.update_receipt()

    def update_receipt(self):
        if not self.bc_receipt_frame.isEnabled():
            self.bc_receipt_list_model = QStandardItemModel(self.bc_receipt_listview)
        self.bc_receipt_frame.setEnabled(True)

        if self.current_product.weigh_b:
            item = QStandardItem(self.bc_name_lbl.text() + ' (' + str(Decimal(self.bc_weight_sbox.value()).quantize(self.cents, ROUND_HALF_UP)) + ' lbs)\n$' + str(
                Decimal(Decimal(self.bc_weight_sbox.value()) * Decimal(self.bc_price_lbl.text())).quantize(self.cents, ROUND_HALF_UP)))
        else:
            item = QStandardItem(self.bc_name_lbl.text() + ' (' + str(self.bc_quantity_sbox.value()) + ')\n$' + str(
                Decimal(int(self.bc_quantity_sbox.value()) * Decimal(self.bc_price_lbl.text())).quantize(self.cents, ROUND_HALF_UP)))
        # item.setCheckable(True)

        self.bc_receipt_list_model.appendRow(item)

        self.bc_receipt_listview.setModel(self.bc_receipt_list_model)

        # Calculate totals
        if self.current_product.weigh_b:
            self.subtotal += Decimal(Decimal(self.bc_weight_sbox.value()).quantize(self.cents, ROUND_HALF_UP) * Decimal(self.bc_price_lbl.text())).quantize(
                self.cents, ROUND_HALF_UP)
            self.tax += Decimal(
                (Decimal(self.bc_weight_sbox.value()).quantize(self.cents, ROUND_HALF_UP) * Decimal(self.bc_price_lbl.text())) * self.tax_rate).quantize(
                self.cents, ROUND_HALF_UP)
            self.total = self.subtotal + self.tax
        else:
            self.subtotal += Decimal(int(self.bc_quantity_sbox.value()) * Decimal(self.bc_price_lbl.text())).quantize(
                self.cents, ROUND_HALF_UP)
            self.tax += Decimal(
                (int(self.bc_quantity_sbox.value()) * Decimal(self.bc_price_lbl.text())) * self.tax_rate).quantize(
                self.cents, ROUND_HALF_UP)
            self.total = self.subtotal + self.tax

        # Update totals labels
        self.bc_r_subtotal_lbl.setText('$' + str(self.subtotal))
        self.bc_tax_lbl.setText('$' + str(self.tax))
        self.bc_total_lbl.setText('$' + str(self.total))

    def handle_remove_item(self):
        """Removes selected item from listview and receipt lists"""
        # print("Before Item Removal")
        # print(str(self.receipt_names))
        # print(str(self.receipt_quantity))
        # print(str(self.receipt_price))
        try:
            row = self.bc_receipt_listview.selectedIndexes()[0].row()
            # print("Row: []".format(row))
            # UPDATE TOTALS
            if isinstance(self.receipt_quantity[row], int):
                self.subtotal -= Decimal(float(self.receipt_quantity[row]) * float(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP)
                self.tax -= Decimal((float(self.receipt_quantity[row]) * float(Decimal(float(self.receipt_price[row])) * self.tax_rate.quantize(self.cents, ROUND_HALF_UP)))).quantize(self.cents, ROUND_HALF_UP)
                self.total -= Decimal(float(self.receipt_quantity[row]) * float(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP) + Decimal((self.receipt_quantity[row] * Decimal(self.receipt_price[row])) * self.tax_rate).quantize(
                    self.cents, ROUND_HALF_UP)
            else:
                self.subtotal -= Decimal(Decimal(self.receipt_quantity[row]) * Decimal(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP)
                self.tax -= Decimal(Decimal(self.receipt_quantity[row]) * Decimal(self.receipt_price[row]) * Decimal(self.tax_rate)).quantize(self.cents, ROUND_HALF_UP)
                self.total -= Decimal(Decimal(self.receipt_quantity[row]) * Decimal(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP) + Decimal(Decimal(self.receipt_quantity[row]) * Decimal(self.receipt_price[row]) * Decimal(self.tax_rate)).quantize( self.cents, ROUND_HALF_UP)

            if self.tax < 0:
                self.tax = Decimal(0).quantize(self.cents, ROUND_HALF_UP)

            # Update totals labels
            self.bc_r_subtotal_lbl.setText('$' + str(self.subtotal))
            self.bc_tax_lbl.setText('$' + str(self.tax))
            self.bc_total_lbl.setText('$' + str(self.total))

            self.bc_receipt_list_model.removeRow(row)
            self.receipt_names.pop(row)
            self.receipt_text.pop(row)
            self.receipt_quantity.pop(row)
            self.receipt_price.pop(row)

            # print("After Item Removal")
            # print(str(self.receipt_names))
            # print(str(self.receipt_quantity))
            # print(str(self.receipt_price))

        except IndexError as e:  # If no items are selected
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))

            self.set_status_style("red")
            self.statusbar.showMessage("***Index Error--Please select an item***", 4000)
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

    def update_inventory(self):
        self.products_table = self.db['products']
        for i in range(0, len(self.receipt_names)):
            prod = self.products_table.find_one(barcode=int(self.receipt_names[i]))
            if prod['weigh_b']:
                new_quantity = Decimal(prod['available_units']).quantize(self.cents, ROUND_HALF_UP) - Decimal(self.receipt_quantity[i]).quantize(self.cents, ROUND_HALF_UP)
            else:
                new_quantity = int(prod['available_units']) - int(self.receipt_quantity[i])
            self.products_table.update(dict(barcode=prod['barcode'], available_units=str(new_quantity)), ['barcode'])

    def launch_payment_dialog(self):
        self.payment_dialog = payment_dialog.PaymentDialog(self, self.bc_current_customer)
        self.payment_dialog.exec_()

    def print_(self, method):
        """ Print the contents of the ConsoleWidget to the specified QPrinter."""
        self.receipt_other.append(datetime.datetime.now().strftime("%m%d%y%H%M%S"))
        self.receipt_other.append(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        self.receipt_other.append(self.employee_id_lbl.text())
        self.receipt_other.append(method)
        self.receipt_other.append(str(Decimal(self.subtotal).quantize(self.cents, ROUND_HALF_UP)))
        self.receipt_other.append(str(Decimal(self.tax).quantize(self.cents, ROUND_HALF_UP)))
        self.receipt_other.append(str(Decimal(self.total).quantize(self.cents, ROUND_HALF_UP)))
        self.receipt_date = datetime.datetime.now().strftime("%m/%d/%Y")
        self.receipt_date_time = int(datetime.datetime.now().timestamp())
        # print(str(self.receipt_date))

        if self.payment_dialog.current_customer is not None:
            customer_id = self.payment_dialog.current_customer.customer_id
        else:
            customer_id = None

        header = "Smith's Grocery\n\n123 ABC Lane\nLogan,UT 84321\n555-435-1234\n\n{}\nCashier: {}\nCustomer ID: {}\nPayment Method: {}\nReceipt ID: {}\n\n_______________________________\n".format(self.receipt_other[1], self.receipt_other[2], customer_id, self.receipt_other[3], self.receipt_other[0])
        footer = "_______________________________\nSubtotal: {}\nTax: {}\n\nTotal: {}".format(self.bc_r_subtotal_lbl.text(), self.bc_tax_lbl.text(), self.bc_total_lbl.text())
        receipt = ""
        receipt += header

        print("Names: " + str(self.receipt_names))
        print("Prices: " + str(self.receipt_price))
        print("Names: " + str(self.receipt_quantity))
        print("Text: " + str(self.receipt_text))
        print("Other: " + str(self.receipt_other))

        for i in range(0, len(self.receipt_names)):
            if isinstance(self.receipt_quantity[i], int):
                receipt += (self.receipt_text[i] + ' (' + str(self.receipt_quantity[i]) + ')' + '\n$' + str(int(self.receipt_quantity[i]) * float(self.receipt_price[i])) + '\n\n')
            else:
                receipt += (self.receipt_text[i] + ' (' + str(self.receipt_quantity[i]) + ' lbs)' + '\n$' + str(Decimal(float(self.receipt_quantity[i]) * float(self.receipt_price[i])).quantize(self.cents, ROUND_HALF_UP)) + '\n\n')
        receipt += footer
        # Appli = QApplication(sys.argv)
        printer = QPrinter()
        doc = QTextDocument(receipt)
        dialog = QPrintDialog(printer)
        dialog.setModal(True)
        dialog.setWindowTitle("Print Receipt")


        # dialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if dialog.exec_() == True:
            try:
                doc.print_(printer)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print("Error: {}, {}, {}".format(exc_type, fname, exc_tb.tb_lineno))
                print("?")
        self.receipts_table = self.db['receipts']
        self.receipts_table.insert(dict(date=str(self.receipt_date), other=str(self.receipt_other), name=str(self.receipt_names), quantity=str(self.receipt_quantity),
                                        price=str(self.receipt_price), text=str(self.receipt_text), r_id=self.receipt_other[0], date_time=self.receipt_date_time, customer_id=customer_id))
        self.update_inventory()
        self.populate_mo_listview()
        self.cancel_transaction()

app = QApplication([])

if __name__ == "__main__":
    main_window = MainWindow()

    app_icon = QtGui.QIcon()
    app_icon.addFile('SmithsLogo.png', QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    main_window.show()
    app.exec_()
