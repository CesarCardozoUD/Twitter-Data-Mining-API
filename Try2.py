import sys
from PyQt5 import uic, QtWidgets

qtCreatorFile = "SecTry.ui" # Nombre del archivo aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):    
        
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.btnMostrar.clicked.connect(self.blah)  
        
    def blah(self):
        user = self.txtUser.toPlainText()
        self.lblResultSet.setText(user)
    

if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())