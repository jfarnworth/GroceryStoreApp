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
        payment_dialog.resize(448, 149)
        payment_dialog.setStyleSheet("#error_lbl {\n"
"    color: red;\n"
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
        self.print_btn.setGeometry(QtCore.QRect(200, 36, 183, 35))
        self.print_btn.setObjectName("print_btn")
        self.total_lbl_2 = QtWidgets.QLabel(payment_dialog)
        self.total_lbl_2.setGeometry(QtCore.QRect(200, 96, 89, 16))
        self.total_lbl_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.total_lbl_2.setObjectName("total_lbl_2")
        self.total_lbl = QtWidgets.QLabel(payment_dialog)
        self.total_lbl.setGeometry(QtCore.QRect(294, 96, 86, 16))
        self.total_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.total_lbl.setObjectName("total_lbl")
        self.error_lbl = QtWidgets.QLabel(payment_dialog)
        self.error_lbl.setGeometry(QtCore.QRect(20, 112, 165, 16))
        self.error_lbl.setText("")
        self.error_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.error_lbl.setObjectName("error_lbl")

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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    payment_dialog = QtWidgets.QDialog()
    ui = Ui_payment_dialog()
    ui.setupUi(payment_dialog)
    payment_dialog.show()
    sys.exit(app.exec_())

