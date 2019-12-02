import os
import shutil
import subprocess
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic

Ui_MainWindow, QtBaseClass = uic.loadUiType("Interface.ui")

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(".res\\app_icon.ico"))
        self.current = 0
        self.btn_num = 0
        self.files_path = []
        self.results = {}
        self.btns = []
        icon = QtGui.QPixmap(".res\\prev.ico")
        self.ui.prev.setIcon(QtGui.QIcon(icon))
        icon = QtGui.QPixmap(".res\\next.ico")
        self.ui.next.setIcon(QtGui.QIcon(icon))
        self.ui.dummy1.setVisible(False)
        self.ui.dummy2.setVisible(False)
        self.ui.dummy3.setVisible(False)
        self.ui.link.setText('<a href="https://github.com/mochatek/">MochaTek.</a>')
        self.ui.link.setOpenExternalLinks(True)

        # Signals and slots
        self.ui.browse.clicked.connect(self.pickFolder)
        self.ui.next.clicked.connect(self.nextImg)
        self.ui.prev.clicked.connect(self.prevImg)
        self.ui.ctgry_group.buttonClicked.connect(self.onClick)
        self.ui.sort.clicked.connect(self.sortFiles)
        self.ui.create.clicked.connect(self.createBtn)
        self.ui.clear.clicked.connect(self.clearBtns)

    def uncheckBtns(self):
        # Uncheck all radio buttons
        self.ui.ctgry_group.setExclusive(False)
        if self.btns:
            for btn in self.btns:
                btn.setChecked(False)
        self.ui.ctgry_group.setExclusive(True)


    def pickFolder(self):
        # Clean UI
        self.ui.loading.clear()
        self.ui.image.clear()
        self.current = 0
        self.btn_num = 0
        self.files_path.clear()
        self.results.clear()
        self.clearBtns()

        # Open dialog for choosing folder
        dialog = QtWidgets.QFileDialog()
        self.folder_path = dialog.getExistingDirectory(None, "Select Images Folder")

        # Add absolute path of all images in the folder to a list
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    self.files_path.append(os.path.join(root,file))
                    self.results[self.files_path[-1]] = None

        # Display first image
        if self.folder_path:
            if self.files_path:
                pixmap = QtGui.QPixmap(self.files_path[self.current])
                self.ui.image.setPixmap(pixmap)
            else:
                self.ui.image.clear()
                self.ui.image.setText("No valid images in the chosen folder !")
        else:
            self.ui.image.clear()
            self.ui.image.setText("SELECT IMAGE FOLDER TO VIEW IMAGE")


    def prevImg(self):
        # Display previous image till first image
        if self.files_path:
            if self.current > 0:
                self.current -= 1
                pixmap = QtGui.QPixmap(self.files_path[self.current])
                self.ui.image.setPixmap(pixmap)

                # Set radiobutton according to choice made
                btn = self.results[self.files_path[self.current]]
                if btn:
                    btn.setChecked(True)
                else:
                    self.uncheckBtns()


    def nextImg(self):
        # Display next image till last image
        if self.files_path:
            if self.current < len(self.files_path) - 1:
                self.current += 1
                pixmap = QtGui.QPixmap(self.files_path[self.current])
                self.ui.image.setPixmap(pixmap)
                btn = self.results[self.files_path[self.current]]
                if btn:
                    btn.setChecked(True)
                else:
                    self.uncheckBtns()


    def onClick(self):
        # Take note of choices made
        if self.files_path:
            btn = self.ui.ctgry_group.checkedButton()
            self.results[self.files_path[self.current]] = btn
            self.nextImg()
        
        
    def sortFiles(self):
        try:
            if self.files_path and self.btns:
                # Show loading GIF
                gif = QtGui.QMovie(".res\\loading.gif")
                self.ui.loading.setMovie(gif)
                gif.start()

                # Create output folders
                try:
                    os.chdir(self.folder_path)
                    os.mkdir("Output")
                except:
                    pass
                os.chdir(self.folder_path + "\\Output")
                
                # Create category folders
                for btn in self.btns:
                    try:
                        os.mkdir(btn.text())
                    except:
                        pass

                # Copy files to corresponding folders
                for img in self.files_path:
                    if self.results[img]:
                        try:
                            shutil.copy(img, self.results[img].text()+"\\")
                        except:
                            pass                
                # Stop loading GIF
                gif.stop()

                # Open Output folder
                subprocess.Popen('explorer ' + os.getcwd())

                # Refresh UI
                self.ui.image.clear()
                self.ui.image.setText("SORTING COMPLETED !")
                self.current = 0
                self.files_path.clear()
                self.results.clear()
                self.uncheckBtns()
                self.clearBtns()
        except Exception as err:
            QtWidgets.QMessageBox.critical(self, "Error", str(err))



    def createBtn(self):
        # Check for validity of folder name
        fname = self.ui.fname.text().strip().upper()
        if fname:
            for ltr in fname:
                if not ltr.isalnum():
                    fname = fname.replace(ltr, "")
            if fname:
                # If valid and no button with same name exist, then create new button
                if fname not in [btn.text() for btn in self.btns]:
                    self.btn_num += 1
                    btn = QtWidgets.QRadioButton(fname)
                    btn.setChecked(False)
                    obname = "btn" + str(self.btn_num)
                    btn.setObjectName(obname)
                    self.ui.ctgry_group.addButton(btn)
                    self.ui.gl.addWidget(btn)
                    
                    # Add new button created to button list
                    self.btns.append(btn)
                    self.ui.fname.clear()
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", "Folder already Exists !")


    def clearBtns(self):
        if self.btns:
            for btn in self.btns:
                btn.deleteLater()
            self.btns.clear()
            self.files_path.clear()
            self.results.clear()
            self.btn_num = 0

                  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())