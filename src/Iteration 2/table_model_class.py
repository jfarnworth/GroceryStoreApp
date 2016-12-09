from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import operator  # used for sorting


class TableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
        self.initial_sort = True

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        if self.mylist != []:
            return len(self.mylist[0])
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return None
        # elif role == Qt.DecorationRole and index.column() == 0:
        #     if index.sibling(index.row(), 2).data() == "Clocked In" \
        #             or index.sibling(index.row(), 2).data() == "Back from Break":
        #         pixmap = QtGui.QPixmap("images/clockedIn.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 2).data() == "Clocked Out":
        #         pixmap = QtGui.QPixmap("images/clockedOut.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 2).data() == "On Break":
        #         pixmap = QtGui.QPixmap("images/onBreak.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 1).data() == "Clocked In" or index.sibling(index.row(), 1).data() == "Back from Break":
        #         pixmap = QtGui.QPixmap("images/mini_clockedIn.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 1).data() == "Clocked Out":
        #         pixmap = QtGui.QPixmap("images/mini_clockedOut.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 1).data() == "On Break":
        #         pixmap = QtGui.QPixmap("images/mini_onBreak.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 1).data() == "PTO" or index.sibling(index.row(), 1).data() == "Vacation" or index.sibling(index.row(), 1).data() == "Sick":
        #         pixmap = QtGui.QPixmap("images/mini_accrual.png")
        #         return pixmap
        #     elif index.sibling(index.row(), 1).data() == "Holiday" or index.sibling(index.row(), 1).data() == "Bereavement" or index.sibling(index.row(), 1).data() == "Other" or index.sibling(index.row(), 1).data() == "No Pay Time":
        #         pixmap = QtGui.QPixmap("images/mini_other.png")
        #         return pixmap
        #     else:
        #         return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        # if orientation == Qt.Horizontal and role == Qt.DecorationRole and col == 0:  # It works,
        # but it shrinks the image and I don't know why
        #     pixmap = QtGui.QPixmap("images/clockedIn.png")
        #     return pixmap
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]

        return None

    def return_first_row(self):
        print(self.mylist[0])

    # def sort(self, col, order):
    #     """sort table by given column number col"""
    #     self.layoutAboutToBeChanged.emit()
    #     # if col == 0 and self.initial_sort:
    #     #     col = 1
    #     # if col != 0:
    #     #     if col == 5:
    #     #         col = 1
    #     #     self.initial_sort = False
    #     #     # self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
    #     #     # self.mylist = sorted(self.mylist)  # , key=operator.itemgetter(col))
    #     #     # print(str(col))
    #     #     self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
    #     #     # TODO: Create sorted methods that will deal with Time, Date, and Comment Columns
    #     #     if order == Qt.AscendingOrder:
    #     #         self.mylist.reverse()
    #     #     if col == 2:
    #     #         self.sort_by_status(order)
    #     #     self.layoutChanged.emit()
    # #     else:
    # #         self.sort_by_status(order)
    # #
    # # def sort_by_status(self, order):
    # #     """sort table by status and then sort alphabetically"""
    # #     self.layoutAboutToBeChanged.emit()
    # #     if order == Qt.AscendingOrder:
    # #         self.mylist = sorted(self.mylist, key=lambda employee: (employee[2], employee[1]))
    # #     else:
    # #         self.mylist = sorted(self.mylist, key=lambda employee: employee[2], reverse=True)
    # #     self.layoutChanged.emit()

    def sort(self, col, order):
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order == Qt.AscendingOrder:
            self.mylist.reverse()
        self.layoutChanged.emit()
