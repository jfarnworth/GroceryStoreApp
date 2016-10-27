from ui import smith_ui, login_ui, payment_ui
from classes import employee, product, receipt

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QSplashScreen, QProgressBar, QDialog
import sys
from decimal import Decimal, ROUND_HALF_UP

import dataset
import datetime
import ast

from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrintDialog

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

class PaymentDialog(QtWidgets.QDialog, payment_ui.Ui_payment_dialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.main_window = parent
        self.error_lbl.setText("")
        self.cash_rb.setChecked(True)
        self.total_lbl.setText(self.main_window.bc_total_lbl.text())

        # Connections
        self.print_btn.clicked.connect(self.handle_print_btn)

    def handle_print_btn(self):
        if self.cash_rb.isChecked():
            self.main_window.print_("Cash")
        elif self.credit_rb.isChecked():
            self.main_window.print_("Credit Card")
        elif self.check_rb.isChecked():
            self.main_window.print_("Check")
        self.close()


class LoginDialog(QtWidgets.QDialog, login_ui.Ui_login_dialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
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
        self.setWindowIcon(QtGui.QIcon('48x48.png'))
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        self.double_validator = QtGui.QDoubleValidator()
        self.int_validator = QtGui.QIntValidator()

        self.setWindowIcon(QtGui.QIcon('SmithsLogo.png'))

        # connecting to a SQLite database
        self.db = dataset.connect('sqlite:///smith.db')
        print("Connected " + str(self.db))
        self.employees_table = self.db['employees']
        # Insert admin record
        try:
            self.employees_table.insert(dict(id=0, name="admin", password="system", role=0))
        except:
            print("Database Exists")

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
        self.current_product = None
        self.mp_new_product_b = False
        self.mp_barcode_search_field.setValidator(self.int_validator)
        self.mp_barcode_field.setValidator(self.int_validator)
        self.mp_available_units_field.setValidator(self.double_validator)
        self.mp_price_field.setValidator(self.double_validator)
        self.mp_customer_price_field.setValidator(self.double_validator)
        self.mp_provider_field.setValidator(self.int_validator)

        # Connections
        self.mp_barcode_search_field.returnPressed.connect(self.get_product)
        self.mp_search_btn.clicked.connect(self.get_product)
        self.mp_add_btn.clicked.connect(self.handle_add_new_product)
        self.mp_delete_btn.clicked.connect(self.handle_delete_product)
        self.mp_update_btn.clicked.connect(self.handle_update_product)

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

        #########################################
        # Begin Checkout Initializing
        #########################################
        self.reset_checkout()
        self.receipt_names = []
        self.receipt_text = []
        self.receipt_quantity = []
        self.receipt_price = []
        self.receipt_other = []
        self.cents = Decimal('.01')
        self.tax_rate = Decimal(.047)
        self.subtotal = Decimal(0.0)
        self.tax = Decimal(0.0)
        self.total = Decimal(0.0)
        self.bc_barcode_search_field.setValidator(self.int_validator)
        self.bc_begin_checkout_btn.setFocus()

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
        # self.bc_weight_sbox.returnPressed.connect(self.handle_add_item)

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
        except:
            print("error")
            self.statusbar.showMessage("Error loading employee data", 4000)


    def display_tabs(self):
        """Displays tabs based on user role. Admins have access to Manage Employees/Manage Products/Begin Checkout
        Cashiers only have access to Begin Checkout"""
        self.tabWidget.clear()

        if self.current_employee.role == 0:
            self.tabWidget.insertTab(0, self.begin_checkout_tab, "Begin Checkout")
            self.tabWidget.insertTab(0, self.reports_tab, "Reports")
            self.tabWidget.insertTab(0, self.manage_orders_tab, "Manage Orders")
            self.tabWidget.insertTab(0, self.manage_products_tab, "Manage Products")

            self.tabWidget.insertTab(0, self.manage_employees_tab, "Manage Employees")


            self.populate_me_employee_list_view()

            self.tabWidget.setCurrentIndex(0)
        elif self.current_employee.role == 1:
            self.tabWidget.insertTab(0, self.begin_checkout_tab, "Begin Checkout")
            self.tabWidget.insertTab(0, self.manage_orders_tab, "Manage Orders")
            self.tabWidget.setCurrentIndex(1)

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

    def handle_update_employee(self):
        """Updates employee info"""
        if self.me_name_field.text() != "":
            if self.me_new_employee_b:
                print("Calling DB")  # update new employee
                # get a reference to the table 'user'
                self.employees_table = self.db['employees']
                # Insert a new record
                try:
                    self.employees_table.insert(dict(id=int(self.me_id_lbl.text()), name=self.me_name_field.text(),
                                                     password=self.me_password_field.text(),
                                                     role=self.me_role_cbox.currentIndex()))
                    self.me_new_employee_b = False
                    self.statusbar.showMessage( self.me_name_field.text() + " added to Users", 4000)
                except:
                    self.statusbar.showMessage("Error--" + self.me_name_field.text() + " not added to Users", 4000)

            else:
                self.employees_table = self.db['employees']
                # Update a record
                try:
                    self.employees_table.update(dict(id=int(self.me_id_lbl.text()), name=self.me_name_field.text(),
                                                     password=self.me_password_field.text(),
                                                     role=self.me_role_cbox.currentIndex()), ['id'])
                    self.statusbar.showMessage(self.me_name_field.text() + "\'s information updated", 4000)
                except:
                    self.statusbar.showMessage("Error--" + self.me_name_field.text() + "\'s information not updated", 4000)

            self.get_employees()  # recreate employee list
            self.populate_me_employee_list_view()  # reload employee list view

    def handle_delete_employee(self):
        """Delete employee from database"""
        # TODO: confirmation dialog
        self.employees_table = self.db['employees']
        if self.me_id_lbl.text() != '0':
            try:
                # Delete a record
                self.employees_table.delete(id=int(self.me_id_lbl.text()))
                self.statusbar.showMessage(self.me_name_field.text() + " deleted from Users", 4000)
            except:
                self.statusbar.showMessage("Error--" + self.me_name_field.text() + " not deleted from Users", 4000)

            self.me_id_lbl.setText("")
            self.me_name_field.setText("")
            self.me_password_field.setText("")
            self.me_employee_gbox.setEnabled(False)
            self.me_delete_employee_btn.setEnabled(False)
            self.get_employees()  # recreate employee list
            self.populate_me_employee_list_view()  # reload employee list view

    def populate_employee_info(self):
        """Displays selected employee info"""
        self.me_employee_gbox.setEnabled(True)
        self.me_delete_employee_btn.setEnabled(True)
        self.me_update_employee_btn.setEnabled(True)
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
            self.mp_delete_btn.setEnabled(True)
            self.mp_update_btn.setEnabled(True)
            self.mp_current_product = product.Product(prod['name'], prod['barcode'], prod['available_units'], prod['price'], prod['customer_price'], prod['weigh_b'], prod['provider'])
            self.mp_product_gbox.setEnabled(True)
            self.mp_name_field.setText(self.mp_current_product.name)
            self.mp_barcode_field.setText(str(self.mp_current_product.barcode))
            self.mp_available_units_field.setText(str(self.mp_current_product.available))
            self.mp_price_field.setText(str(self.mp_current_product.price))
            self.mp_customer_price_field.setText(str(self.mp_current_product.customer_price))
            if self.mp_current_product.weigh_b:
                self.mp_weight_rb.setChecked(True)
            else:
                self.mp_quantity_rb.setChecked(True)
            self.mp_provider_field.setText(str(self.mp_current_product.provider))
            self.mp_barcode_search_field.setText("")
        except TypeError:
            self.statusbar.showMessage("Error--Invalid Barcode", 4000)

    def handle_add_new_product(self):
        """Clears product fields so new info can be added"""
        self.mp_new_product_b = True
        self.mp_product_gbox.setEnabled(True)
        self.mp_delete_btn.setEnabled(True)
        self.mp_update_btn.setEnabled(True)
        self.mp_name_field.setText("")
        self.mp_barcode_field.setText("")
        self.mp_available_units_field.setText("")
        self.mp_price_field.setText("")
        self.mp_customer_price_field.setText("")
        self.mp_quantity_rb.setChecked(True)
        self.mp_provider_field.setText("")
        self.mp_current_product = product.Product(self.mp_name_field.text(), self.mp_barcode_field.text(),
                                                  self.mp_available_units_field.text(),
                                                  self.mp_price_field.text(), self.mp_customer_price_field.text(),
                                                  self.mp_quantity_rb.isChecked(), self.mp_provider_field.text())

    def handle_update_product(self):
        """Updates employee info"""
        if self.mp_name_field.text() != "" and self.mp_barcode_field.text() != "" and self.mp_available_units_field.text() != "" and self.mp_price_field.text() != "" and self.mp_customer_price_field.text() != "" and self.mp_provider_field.text() != "":
            if self.mp_new_product_b:
                self.products_table = self.db['products']
                if self.mp_quantity_rb.isChecked():
                    weigh = 0
                else:
                    weigh = 1
                # Update a record
                try:
                    self.products_table.insert(dict(name=self.mp_name_field.text(), barcode=int(self.mp_barcode_field.text()),
                                                    available_units=self.mp_available_units_field.text(),
                                                    price=self.mp_price_field.text(),
                                               customer_price=self.mp_customer_price_field.text(),
                                               weigh_b=weigh, provider=self.mp_provider_field.text())) # ValueError: invalid literal for int() with base 10: ''
                    self.mp_new_product_b = False
                    self.statusbar.showMessage(self.mp_name_field.text() + " added to Products Database", 4000)
                except:
                    print("Error adding new item")
                    self.statusbar.showMessage("Error--" + self.mp_name_field.text() + " not added to Products Database", 4000)
            else:
                self.products_table = self.db['products']
                if self.mp_quantity_rb.isChecked():
                    weigh = 0
                else:
                    weigh = 1
                try:
                    self.products_table.update(dict(name=self.mp_name_field.text(), barcode=int(self.mp_barcode_field.text()),
                                                    available_units=self.mp_available_units_field.text(),
                                                    price=self.mp_price_field.text(),
                                                    customer_price=self.mp_customer_price_field.text(),
                                                    weigh_b=weigh, provider=self.mp_provider_field.text()), ['barcode']) # ValueError: invalid literal for int() with base 10: ''
                    self.statusbar.showMessage(self.mp_name_field.text() + " information updated", 4000)
                except:
                    print("Error updating item")
                    self.statusbar.showMessage("Error--" + self.mp_name_field.text() + "\'s information not updated", 4000)

    def handle_delete_product(self):
        """Delete employee from database"""
        # TODO: confirmation dialog
        self.products_table = self.db['products']
        try:
            self.products_table.delete(barcode=int(self.mp_barcode_field.text()))
            self.statusbar.showMessage(self.mp_name_field.text() + " deleted from Product Database", 4000)
        except:
            self.statusbar.showMessage("Error--" + self.mp_name_field.text() + " not deleted from Product Database", 4000)
        self.mp_name_field.setText("")
        self.mp_barcode_field.setText("")
        self.mp_available_units_field.setText("")
        self.mp_price_field.setText("")
        self.mp_customer_price_field.setText("")
        self.mp_quantity_rb.setChecked(True)
        self.mp_provider_field.setText("")
        self.mp_product_gbox.setEnabled(False)
        self.mp_delete_btn.setEnabled(False)
        self.mp_update_btn.setEnabled(False)

    #########################################
    # Manage Orders Functions
    #########################################
    def initialize_manage_orders_tab(self):
        self.mo_date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.mo_date_lbl.setText(str(self.mo_date_edit.date().toString("MMMM dd, yyyy")))
        print("Manage Order init")

    def populate_mo_listview(self):
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
        # self.current_receipt = None
        self.mo_receipt_frame.setEnabled(True)
        self.current_receipt = self.receipt_list[self.mo_receipt_date_listview.selectedIndexes()[0].row()]

        self.mo_r_id_lbl.setText(str(self.current_receipt.other[0]))
        self.mo_r_date_lbl.setText(str(self.current_receipt.other[1]))
        emply = self.employees_table.find_one(id=self.current_receipt.other[2])
        self.mo_r_cashier_lbl.setText(str(emply['name']))
        self.mo_r_method_lbl.setText(str(self.current_receipt.other[3]))

        print(str(self.current_receipt.other))

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

            print(str(self.current_receipt.other))

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
        except:
            self.statusbar.showMessage("Search Error--Please enter a valid Receipt ID", 4000)



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

        except IndexError:  # If no items are selected
            self.statusbar.showMessage("Index Error--Please select an item", 4000)

    def mo_update_inventory(self, row):
        try:
            # print("Row #:" + str(row))
            # print("Why are you not working?")
            # print(str(self.current_receipt.names))
            # print("Product Barcode: " + str(self.current_receipt.names[row]))
            self.products_table = self.db['products']
            # print("Successful connection to product db")
            prod = self.products_table.find_one(barcode=int(self.current_receipt.names[row]))
            # print("Successful prodcut barcode: " + str(prod['name']))
            if prod['weigh_b']:
                new_quantity = Decimal(prod['available_units']).quantize(self.cents, ROUND_HALF_UP) + Decimal(self.current_receipt.quantity[row]).quantize(self.cents, ROUND_HALF_UP)
            else:
                new_quantity = int(prod['available_units']) + self.current_receipt.quantity[row]
            self.products_table.update(dict(barcode=prod['barcode'], available_units=str(new_quantity)), ['barcode'])

        except:
            self.statusbar.showMessage("Error updating inventory", 4000)
            print("Error updating inventory")

    def mo_update_receipt(self):
        print("Updating receipt")
        self.receipts_table = self.db['receipts']
        self.receipts_table.update(dict(other=str(self.current_receipt.other), name=str(self.current_receipt.names), quantity=str(self.current_receipt.quantity), price=str(self.current_receipt.price), text=str(self.current_receipt.text), r_id=self.current_receipt.other[0]), ['r_id'])

    #########################################
    # Reports Functions
    #########################################

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

    def enable_remove_btn(self):
        self.bc_remove_btn.setEnabled(True)

    def reset_checkout(self):
        """Show checkout frame"""
        self.bc_checkout_frame.setHidden(True)

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
        except:
            self.statusbar.showMessage("Invalid Barcode", 4000)

    def calculate_item_subtotal(self):
        try:
            if self.current_product.weigh_b:
                self.bc_subtotal_lbl.setText(str(Decimal(self.bc_weight_sbox.value() * self.current_product.customer_price).quantize(self.cents, ROUND_HALF_UP)))
            else:
                self.bc_subtotal_lbl.setText(str(Decimal(self.bc_quantity_sbox.value() * self.current_product.customer_price).quantize(self.cents, ROUND_HALF_UP)))
        except:
            print("Error")

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
            item = QStandardItem(self.bc_name_lbl.text() + ' (' + str(Decimal(self.bc_weight_sbox.value()).quantize(self.cents,
                                                                                                           ROUND_HALF_UP)) + ' lbs)\n$' + str(
                Decimal(Decimal(self.bc_weight_sbox.value()) * Decimal(self.bc_price_lbl.text())).quantize(self.cents,
                                                                                                           ROUND_HALF_UP)))
        else:
            item = QStandardItem(self.bc_name_lbl.text() + ' (' + str(self.bc_quantity_sbox.value()) + ')\n$' + str(
                Decimal(int(self.bc_quantity_sbox.value()) * Decimal(self.bc_price_lbl.text())).quantize(self.cents,
                                                                                                         ROUND_HALF_UP)))
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
        print("Before Item Removal")
        print(str(self.receipt_names))
        print(str(self.receipt_quantity))
        print(str(self.receipt_price))

        try:
            row = self.bc_receipt_listview.selectedIndexes()[0].row()

            # UPDATE TOTALS
            if isinstance(self.receipt_quantity[row], int):
                self.subtotal -= Decimal(float(self.receipt_quantity[row]) * float(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP)
                self.tax -= Decimal((float(self.receipt_quantity[row]) * float(Decimal(float(self.receipt_price[row])) * self.tax_rate.quantize(self.cents, ROUND_HALF_UP)))).quantize(self.cents, ROUND_HALF_UP)
                self.total -= Decimal(float(self.receipt_quantity[row]) * float(self.receipt_price[row])).quantize(self.cents, ROUND_HALF_UP) + Decimal((self.receipt_quantity[row] * Decimal(self.receipt_price[row])) * self.tax_rate).quantize(
                    self.cents, ROUND_HALF_UP)
            else:
                self.subtotal -= Decimal(int(self.receipt_quantity[row]) * self.receipt_price[row]).quantize(self.cents,
                                                                                                             ROUND_HALF_UP)
                self.tax -= Decimal(
                    (int(self.receipt_quantity[row]) * Decimal(self.receipt_price[row])) * self.tax_rate).quantize(
                    self.cents, ROUND_HALF_UP)
                self.total -= Decimal(int(self.receipt_quantity[row]) * self.receipt_price[row]).quantize(self.cents,
                                                                                                          ROUND_HALF_UP) + Decimal(
                    (int(self.receipt_quantity[row]) * Decimal(self.receipt_price[row])) * self.tax_rate).quantize(
                    self.cents, ROUND_HALF_UP)

            # Update totals labels
            self.bc_r_subtotal_lbl.setText('$' + str(self.subtotal))
            self.bc_tax_lbl.setText('$' + str(self.tax))
            self.bc_total_lbl.setText('$' + str(self.total))

            self.bc_receipt_list_model.removeRow(row)
            self.receipt_names.pop(row)
            self.receipt_text.pop(row)
            self.receipt_quantity.pop(row)
            self.receipt_price.pop(row)

            print("After Item Removal")
            print(str(self.receipt_names))
            print(str(self.receipt_quantity))
            print(str(self.receipt_price))

        except IndexError:  # If no items are selected
            self.statusbar.showMessage("Index Error--Please select an item", 4000)

    def update_inventory(self):
        self.products_table = self.db['products']
        for i in range(0, len(self.receipt_names)):
            prod = self.products_table.find_one(barcode=int(self.receipt_names[i]))
            if prod['weigh_b']:
                new_quantity = Decimal(prod['available_units']).quantize(self.cents, ROUND_HALF_UP) - Decimal(self.receipt_quantity[i]).quantize(self.cents, ROUND_HALF_UP)
            else:
                new_quantity = int(prod['available_units']) - self.receipt_quantity[i]
            self.products_table.update(dict(barcode=prod['barcode'], available_units=str(new_quantity)), ['barcode'])

    def launch_payment_dialog(self):
        self.payment_dialog = PaymentDialog(self)
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
        print(str(self.receipt_date))

        header = "Smith's Grocery\n\n123 ABC Lane\nLogan,UT 84321\n555-435-1234\n\n{}\nCashier: {}\nPayment Method: {}\nReceipt ID: {}\n\n_______________________________\n".format(self.receipt_other[1], self.receipt_other[2], self.receipt_other[3], self.receipt_other[0])
        footer = "_______________________________\nSubtotal: {}\nTax: {}\n\nTotal: {}".format(self.bc_r_subtotal_lbl.text(), self.bc_tax_lbl.text(), self.bc_total_lbl.text())
        receipt = ""
        receipt += header
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
        print("Names: " + str(self.receipt_names))
        print("Prices: " + str(self.receipt_price))
        print("Names: " + str(self.receipt_quantity))
        print("Text: " + str(self.receipt_text))
        print("Other: " + str(self.receipt_other))

        # dialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if dialog.exec_() == True:
            try:
                doc.print_(printer)
            except:
                print("?")
        self.receipts_table = self.db['receipts']
        self.receipts_table.insert(dict(date=str(self.receipt_date), other=str(self.receipt_other), name=str(self.receipt_names), quantity=str(self.receipt_quantity), price=str(self.receipt_price), text=str(self.receipt_text), r_id=self.receipt_other[0]))
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
