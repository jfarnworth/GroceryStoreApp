from ui import caution_ui
from PyQt5 import QtWidgets, QtCore

class CautionDialog(QtWidgets.QDialog, caution_ui.Ui_caution_dialog):
    def __init__(self, parent, msg="This action is permanent and CANNOT BE UNDONE."):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.permanent_lbl.setText(msg)
        self.msg = msg
        self.delete_b=False

        # Connections
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def delete_btn_clicked(self):
        # if self.msg == "Deleting an employee CANNOT BE UNDONE.":
        self.delete_b = True
        self.close()

    def cancel_btn_clicked(self):
        self.delete_b = False
        self.close()

            # self.close()
        #elif self.msg == "Deleting a job CANNOT BE UNDONE.":
            # self.employees_in_deleted_job = []
            # for row in range(self.admin_options_dialog.job_record_assigned_employees_model.rowCount()):
            #     item = self.admin_options_dialog.job_record_assigned_employees_model.item(row)
            #     if item.checkState() == QtCore.Qt.Checked:
            #         for employee in self.admin_options_dialog.main_window.db.active_employee_list:
            #             if employee.comma_name == str(item.data(0)):
            #                 self.employees_in_deleted_job.append(int(employee.system_id))
            # print("Employees to be removed from deleted job: " + str(self.employees_in_deleted_job))
            #
            # data = {'job_id': self.admin_options_dialog.job_numb, 'user_ids': str(self.employees_in_deleted_job)}
            # print(str(self.admin_options_dialog.main_window.db.remove_employees_from_deleted_job(data)) + " successfully had employees removed")
            # print(str(self.admin_options_dialog.main_window.db.delete_job(data)) + " was successfully deleted")
            #
            # self.admin_options_dialog.job_tab.setHidden(True)
            # self.admin_options_dialog.toggle_navigation()
            # self.admin_options_dialog.main_window.view.update_all_jobs_models()
            # self.admin_options_dialog.job_name_field.setText("")
            # self.admin_options_dialog.employees_tab.setHidden(False)
            # self.close()
