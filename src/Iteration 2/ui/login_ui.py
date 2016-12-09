# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_login_dialog(object):
    def setupUi(self, login_dialog):
        login_dialog.setObjectName("login_dialog")
        login_dialog.resize(247, 149)
        login_dialog.setStyleSheet("#error_lbl {\n"
"    color: red;\n"
"}")
        self.password_field = QtWidgets.QLineEdit(login_dialog)
        self.password_field.setGeometry(QtCore.QRect(35, 52, 177, 20))
        self.password_field.setText("")
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_field.setObjectName("password_field")
        self.sign_in_btn = QtWidgets.QPushButton(login_dialog)
        self.sign_in_btn.setGeometry(QtCore.QRect(108, 108, 101, 31))
        self.sign_in_btn.setObjectName("sign_in_btn")
        self.employee_id_field = QtWidgets.QLineEdit(login_dialog)
        self.employee_id_field.setGeometry(QtCore.QRect(35, 20, 177, 20))
        self.employee_id_field.setText("")
        self.employee_id_field.setObjectName("employee_id_field")
        self.error_lbl = QtWidgets.QLabel(login_dialog)
        self.error_lbl.setGeometry(QtCore.QRect(36, 82, 175, 16))
        self.error_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.error_lbl.setObjectName("error_lbl")

        self.retranslateUi(login_dialog)
        QtCore.QMetaObject.connectSlotsByName(login_dialog)

    def retranslateUi(self, login_dialog):
        _translate = QtCore.QCoreApplication.translate
        login_dialog.setWindowTitle(_translate("login_dialog", "Dialog"))
        self.password_field.setPlaceholderText(_translate("login_dialog", "Password"))
        self.sign_in_btn.setText(_translate("login_dialog", "Sign In"))
        self.employee_id_field.setPlaceholderText(_translate("login_dialog", "Employee ID"))
        self.error_lbl.setText(_translate("login_dialog", "Incorrect ID or Password."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login_dialog = QtWidgets.QDialog()
    ui = Ui_login_dialog()
    ui.setupUi(login_dialog)
    login_dialog.show()
    sys.exit(app.exec_())

