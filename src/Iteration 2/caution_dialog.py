from ui import caution_ui
from PyQt5 import QtWidgets, QtCore
import requests

class CautionDialog(QtWidgets.QDialog, caution_ui.Ui_caution_dialog):
    def __init__(self, parent, msg="This action is permanent and CANNOT BE UNDONE."):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.admin_options_dialog = parent
        self.permanent_lbl.setText(msg)
        self.msg = msg

        # Connections
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.cancel_btn.clicked.connect(self.close)

    def delete_btn_clicked(self):
        if self.msg == "Deleting a department CANNOT BE UNDONE.":
            self.employees_in_deleted_dept = []
            for row in range(self.admin_options_dialog.ed_assign_employees_model.rowCount()):
                item = self.admin_options_dialog.ed_assign_employees_model.item(row)
                if item.checkState() == QtCore.Qt.Checked:
                    for employee in self.admin_options_dialog.main_window.db.active_employee_list:
                        if employee.comma_name == str(item.data(0)):
                            self.employees_in_deleted_dept.append(int(employee.system_id))
            print("Employees to be removed from deleted dept: " + str(self.employees_in_deleted_dept))

            data={'dept_id': self.admin_options_dialog.department_record_info.json()['Success'][0][0], 'user_ids': str(self.employees_in_deleted_dept)}
            self.admin_options_dialog.main_window.db.delete_update_employee_depts(data)

            data={'name': self.admin_options_dialog.department_record_info.json()['Success'][0][1], 'dept_id': self.admin_options_dialog.department_record_info.json()['Success'][0][0]}
            self.admin_options_dialog.main_window.db.delete_department(data)

            # TODO: Delete department from each employee's department list
            # self.admin_options_dialog.ed_back_btn_clicked()
            self.admin_options_dialog.department_tab.setHidden(True)
            self.admin_options_dialog.toggle_navigation()
            self.admin_options_dialog.main_window.view.update_all_department_models()
            self.admin_options_dialog.dept_name_num_field.setText("")
            self.admin_options_dialog.employees_tab.setHidden(False)

            self.close()
        elif self.msg == "Deleting a job CANNOT BE UNDONE.":
            self.employees_in_deleted_job = []
            for row in range(self.admin_options_dialog.job_record_assigned_employees_model.rowCount()):
                item = self.admin_options_dialog.job_record_assigned_employees_model.item(row)
                if item.checkState() == QtCore.Qt.Checked:
                    for employee in self.admin_options_dialog.main_window.db.active_employee_list:
                        if employee.comma_name == str(item.data(0)):
                            self.employees_in_deleted_job.append(int(employee.system_id))
            print("Employees to be removed from deleted job: " + str(self.employees_in_deleted_job))

            data = {'job_id': self.admin_options_dialog.job_numb, 'user_ids': str(self.employees_in_deleted_job)}
            print(str(self.admin_options_dialog.main_window.db.remove_employees_from_deleted_job(data)) + " successfully had employees removed")
            print(str(self.admin_options_dialog.main_window.db.delete_job(data)) + " was successfully deleted")

            self.admin_options_dialog.job_tab.setHidden(True)
            self.admin_options_dialog.toggle_navigation()
            self.admin_options_dialog.main_window.view.update_all_jobs_models()
            self.admin_options_dialog.job_name_field.setText("")
            self.admin_options_dialog.employees_tab.setHidden(False)
            self.close()
