from GUI import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = myUI()
    gui.show()
    sys.exit(app.exec_())
