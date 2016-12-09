# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'caution.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_caution_dialog(object):
    def setupUi(self, caution_dialog):
        caution_dialog.setObjectName("caution_dialog")
        caution_dialog.resize(400, 169)
        caution_dialog.setStyleSheet("#caution_lbl {\n"
"    color: red;\n"
"    font-size: 20px;\n"
"}")
        self.cancel_btn = QtWidgets.QPushButton(caution_dialog)
        self.cancel_btn.setGeometry(QtCore.QRect(305, 125, 75, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancel_btn.sizePolicy().hasHeightForWidth())
        self.cancel_btn.setSizePolicy(sizePolicy)
        self.cancel_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.cancel_btn.setObjectName("cancel_btn")
        self.delete_btn = QtWidgets.QPushButton(caution_dialog)
        self.delete_btn.setGeometry(QtCore.QRect(225, 125, 75, 23))
        self.delete_btn.setObjectName("delete_btn")
        self.permanent_lbl = QtWidgets.QLabel(caution_dialog)
        self.permanent_lbl.setGeometry(QtCore.QRect(25, 55, 356, 16))
        self.permanent_lbl.setObjectName("permanent_lbl")
        self.proceed_lbl = QtWidgets.QLabel(caution_dialog)
        self.proceed_lbl.setGeometry(QtCore.QRect(25, 75, 356, 16))
        self.proceed_lbl.setObjectName("proceed_lbl")
        self.caution_lbl = QtWidgets.QLabel(caution_dialog)
        self.caution_lbl.setGeometry(QtCore.QRect(25, 25, 356, 26))
        font = QtGui.QFont()
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.caution_lbl.setFont(font)
        self.caution_lbl.setObjectName("caution_lbl")

        self.retranslateUi(caution_dialog)
        QtCore.QMetaObject.connectSlotsByName(caution_dialog)

    def retranslateUi(self, caution_dialog):
        _translate = QtCore.QCoreApplication.translate
        caution_dialog.setWindowTitle(_translate("caution_dialog", "Caution"))
        self.cancel_btn.setText(_translate("caution_dialog", "Cancel"))
        self.delete_btn.setText(_translate("caution_dialog", "Delete"))
        self.permanent_lbl.setText(_translate("caution_dialog", "This action is permanent and CANNOT BE UNDONE."))
        self.proceed_lbl.setText(_translate("caution_dialog", "Would you like to proceed?"))
        self.caution_lbl.setText(_translate("caution_dialog", "Proceed with Caution"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    caution_dialog = QtWidgets.QDialog()
    ui = Ui_caution_dialog()
    ui.setupUi(caution_dialog)
    caution_dialog.show()
    sys.exit(app.exec_())

