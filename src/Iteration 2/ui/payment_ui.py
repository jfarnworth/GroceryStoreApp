# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'payment.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_payment_dialog(object):
    def setupUi(self, payment_dialog):
        payment_dialog.setObjectName("payment_dialog")
        payment_dialog.resize(625, 301)
        payment_dialog.setStyleSheet("#error_lb, #pay_with_points_lbl {\n"
"    color: red;\n"
"}\n"
"\n"
"#total_lbl, #total_lbl_2 {\n"
"    font-size: 16px;\n"
"}")
        self.cash_rb = QtWidgets.QRadioButton(payment_dialog)
        self.cash_rb.setGeometry(QtCore.QRect(39, 36, 82, 17))
        self.cash_rb.setChecked(True)
        self.cash_rb.setObjectName("cash_rb")
        self.credit_rb = QtWidgets.QRadioButton(payment_dialog)
        self.credit_rb.setGeometry(QtCore.QRect(39, 56, 82, 17))
        self.credit_rb.setObjectName("credit_rb")
        self.check_rb = QtWidgets.QRadioButton(payment_dialog)
        self.check_rb.setGeometry(QtCore.QRect(39, 76, 82, 17))
        self.check_rb.setObjectName("check_rb")
        self.print_btn = QtWidgets.QPushButton(payment_dialog)
        self.print_btn.setGeometry(QtCore.QRect(414, 33, 183, 35))
        self.print_btn.setObjectName("print_btn")
        self.total_lbl_2 = QtWidgets.QLabel(payment_dialog)
        self.total_lbl_2.setGeometry(QtCore.QRect(362, 73, 89, 27))
        self.total_lbl_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.total_lbl_2.setObjectName("total_lbl_2")
        self.total_lbl = QtWidgets.QLabel(payment_dialog)
        self.total_lbl.setGeometry(QtCore.QRect(456, 73, 137, 27))
        self.total_lbl.setStyleSheet("")
        self.total_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.total_lbl.setObjectName("total_lbl")
        self.error_lbl = QtWidgets.QLabel(payment_dialog)
        self.error_lbl.setGeometry(QtCore.QRect(20, 112, 273, 16))
        self.error_lbl.setText("")
        self.error_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.error_lbl.setObjectName("error_lbl")
        self.load_customer_info_btn = QtWidgets.QPushButton(payment_dialog)
        self.load_customer_info_btn.setGeometry(QtCore.QRect(414, 224, 183, 35))
        self.load_customer_info_btn.setObjectName("load_customer_info_btn")
        self.customer_name_field = QtWidgets.QLineEdit(payment_dialog)
        self.customer_name_field.setGeometry(QtCore.QRect(414, 148, 183, 20))
        self.customer_name_field.setClearButtonEnabled(True)
        self.customer_name_field.setObjectName("customer_name_field")
        self.customer_id_field = QtWidgets.QLineEdit(payment_dialog)
        self.customer_id_field.setGeometry(QtCore.QRect(414, 174, 183, 20))
        self.customer_id_field.setClearButtonEnabled(True)
        self.customer_id_field.setObjectName("customer_id_field")
        self.points_rb = QtWidgets.QRadioButton(payment_dialog)
        self.points_rb.setEnabled(False)
        self.points_rb.setGeometry(QtCore.QRect(39, 96, 82, 17))
        self.points_rb.setObjectName("points_rb")
        self.available_points_lbl = QtWidgets.QLabel(payment_dialog)
        self.available_points_lbl.setGeometry(QtCore.QRect(122, 186, 86, 16))
        self.available_points_lbl.setText("")
        self.available_points_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.available_points_lbl.setObjectName("available_points_lbl")
        self.available_points_lbl_2 = QtWidgets.QLabel(payment_dialog)
        self.available_points_lbl_2.setGeometry(QtCore.QRect(28, 186, 89, 16))
        self.available_points_lbl_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.available_points_lbl_2.setObjectName("available_points_lbl_2")
        self.pay_with_points_lbl = QtWidgets.QLabel(payment_dialog)
        self.pay_with_points_lbl.setGeometry(QtCore.QRect(104, 96, 223, 16))
        self.pay_with_points_lbl.setStyleSheet("")
        self.pay_with_points_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pay_with_points_lbl.setObjectName("pay_with_points_lbl")
        self.check_rb_2 = QtWidgets.QCheckBox(payment_dialog)
        self.check_rb_2.setGeometry(QtCore.QRect(470, 198, 125, 17))
        self.check_rb_2.setCheckable(True)
        self.check_rb_2.setObjectName("check_rb_2")
        self.available_points_lbl_3 = QtWidgets.QLabel(payment_dialog)
        self.available_points_lbl_3.setGeometry(QtCore.QRect(28, 150, 89, 16))
        self.available_points_lbl_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.available_points_lbl_3.setObjectName("available_points_lbl_3")
        self.customer_name_lbl = QtWidgets.QLabel(payment_dialog)
        self.customer_name_lbl.setGeometry(QtCore.QRect(122, 150, 235, 16))
        self.customer_name_lbl.setText("")
        self.customer_name_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.customer_name_lbl.setObjectName("customer_name_lbl")
        self.customer_id_lbl = QtWidgets.QLabel(payment_dialog)
        self.customer_id_lbl.setGeometry(QtCore.QRect(122, 168, 235, 16))
        self.customer_id_lbl.setText("")
        self.customer_id_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.customer_id_lbl.setObjectName("customer_id_lbl")
        self.available_points_lbl_6 = QtWidgets.QLabel(payment_dialog)
        self.available_points_lbl_6.setGeometry(QtCore.QRect(28, 168, 89, 16))
        self.available_points_lbl_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.available_points_lbl_6.setObjectName("available_points_lbl_6")

        self.retranslateUi(payment_dialog)
        QtCore.QMetaObject.connectSlotsByName(payment_dialog)

    def retranslateUi(self, payment_dialog):
        _translate = QtCore.QCoreApplication.translate
        payment_dialog.setWindowTitle(_translate("payment_dialog", "Dialog"))
        self.cash_rb.setText(_translate("payment_dialog", "Cash"))
        self.credit_rb.setText(_translate("payment_dialog", "Credit Card"))
        self.check_rb.setText(_translate("payment_dialog", "Check"))
        self.print_btn.setText(_translate("payment_dialog", "Print Receipt"))
        self.total_lbl_2.setText(_translate("payment_dialog", "Total"))
        self.total_lbl.setText(_translate("payment_dialog", "$"))
        self.load_customer_info_btn.setText(_translate("payment_dialog", "Load Customer Info"))
        self.customer_name_field.setPlaceholderText(_translate("payment_dialog", "Customer Name"))
        self.customer_id_field.setPlaceholderText(_translate("payment_dialog", "Customer ID"))
        self.points_rb.setText(_translate("payment_dialog", "Points"))
        self.available_points_lbl_2.setText(_translate("payment_dialog", "Available Points"))
        self.pay_with_points_lbl.setText(_translate("payment_dialog", "Customer is not able to pay with points"))
        self.check_rb_2.setText(_translate("payment_dialog", "Create New Customer"))
        self.available_points_lbl_3.setText(_translate("payment_dialog", "Customer Name"))
        self.available_points_lbl_6.setText(_translate("payment_dialog", "Customer ID"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    payment_dialog = QtWidgets.QDialog()
    ui = Ui_payment_dialog()
    ui.setupUi(payment_dialog)
    payment_dialog.show()
    sys.exit(app.exec_())

