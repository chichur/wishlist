import sys
import design
import pymysql
from PyQt5 import QtWidgets
from pymysql.cursors import DictCursor
from pymysql.err import IntegrityError

connection = pymysql.connect(
    host='localhost',
    user='test',
    password='Test1234',
    db='public',
    charset='utf8mb4',
    cursorclass=DictCursor
)


class ExampleApp(QtWidgets.QMainWindow, design.Ui_Dialog):
    def __init__(self):
        self.records = []
        super().__init__()
        self.setupUi(self)
        self.createButton.clicked.connect(self.create_wish)
        self.editButton.clicked.connect(self.update_wish)
        self.deleteButton.clicked.connect(self.delete_wish)
        self.listWidget.itemClicked.connect(self.select_item)
        self.refresh()

    def select_item(self):
        item = self.listWidget.currentItem().text()
        for rec in self.records:
            if rec["name"] == item:
                self.nameEdit.setPlainText(rec["name"])
                self.costEdit.setPlainText(rec["cost"])
                self.linkEdit.setPlainText(rec["link"])
                self.remarkEdit.setPlainText(rec["remark"])

    def create_wish(self):
        with connection.cursor() as cursor:
            query = "INSERT INTO public.wishlist VALUES('{0}', '{1}', '{2}', '{3}');" \
                .format(self.nameEdit.toPlainText(),
                        self.costEdit.toPlainText(),
                        self.linkEdit.toPlainText(),
                        self.remarkEdit.toPlainText())
            try:
                cursor.execute(query)
                connection.commit()
            except IntegrityError:
                error_msg("duplicate_error")
            except Exception as e:
                error_msg(msg=e)
        self.refresh()

    def update_wish(self):
        with connection.cursor() as cursor:
            try:
                query = "UPDATE wishlist SET " \
                        "name='{0}'," \
                        "cost='{1}'," \
                        "link='{2}'," \
                        "remark='{3}'" \
                        "WHERE name='{4}';" \
                    .format(self.nameEdit.toPlainText(),
                            self.costEdit.toPlainText(),
                            self.linkEdit.toPlainText(),
                            self.remarkEdit.toPlainText(),
                            self.listWidget.currentItem().text())
                cursor.execute(query)
                connection.commit()
            except AttributeError:
                error_msg("select_error")
            except Exception as e:
                error_msg(msg=e)
        self.refresh()

    def delete_wish(self):
        with connection.cursor() as cursor:
            try:
                text = self.listWidget.currentItem().text()
                query = "DELETE FROM wishlist WHERE name = '{0}'" \
                    .format(text)
                cursor.execute(query)
                connection.commit()
            except AttributeError as e:
                error_msg("select_error")
            except Exception as e:
                error_msg(msg=e)
        self.refresh()

    def refresh(self):
        self.records.clear()
        self.listWidget.clear()
        with connection.cursor() as cursor:
            query = "SELECT * FROM wishlist"
            try:
                cursor.execute(query)
            except:
                query = "CREATE TABLE wishlist (name VARCHAR(20) UNIQUE, cost VARCHAR(20), " \
                        "link VARCHAR(200), remark VARCHAR(200));"
                cursor.execute(query)

            for row in cursor:
                self.records.append(row)
                self.listWidget.addItem(row['name'])

        self.nameEdit.setPlainText('')
        self.costEdit.setPlainText('')
        self.linkEdit.setPlainText('')
        self.remarkEdit.setPlainText('')


def error_msg(error=None, msg=None):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    if error == "select_error":
        msg_box.setText("Выделите элемент списка")
    elif error == "duplicate_error":
        msg_box.setText("У вас уже есть желание с таким именем")
    else:
        msg_box.setText("Неизвестная ошибка :" + msg)
    msg_box.setWindowTitle("Ошибка")
    msg_box.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
