from PyQt5.QtWidgets import QLineEdit, QDialog, QDialogButtonBox, QFormLayout

class SphereDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Input centre of sphere")

        self.x1 = QLineEdit(self)
        self.y1 = QLineEdit(self)
        self.z1 = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("X", self.x1)
        layout.addRow("Y", self.y1)
        layout.addRow("Z", self.z1)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.x1.text(), self.y1.text(), self.z1.text())

#Клас діалогового вікна для точки
class PointDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.x1 = QLineEdit(self)
        self.y1 = QLineEdit(self)
        self.z1 = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("X", self.x1)
        layout.addRow("Y", self.y1)
        layout.addRow("Z", self.z1)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    #Функція, що повертає введені користувачем дані
    def getInputs(self):
        return [float(i) for i in (self.x1.text(), self.y1.text(), self.z1.text())]
    
#Клас діалогового вікна для функції
class FunctionDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.function = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("function", self.function)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
 
    #Функція, що повертає введені користувачем дані
    def getInputs(self):
        return self.function.text()

#Клас діалогового вікна для вектора
class VectorLineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.m = QLineEdit(self)
        self.n = QLineEdit(self)
        self.p = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("M", self.m)
        layout.addRow("N", self.n)
        layout.addRow("P", self.p)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    #Функція, що повертає введені користувачем дані
    def getInputs(self):
        return [float(i) for i in (self.m.text(), self.n.text(), self.p.text())]

#Клас діалогового вікна для параметричної функції
class ParameterDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.m = QLineEdit(self)
        self.n = QLineEdit(self)
        self.p = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("x(t)=", self.m)
        layout.addRow("y(t)=", self.n)
        layout.addRow("z(t)=", self.p)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    #Функція, що повертає введені користувачем дані
    def getInputs(self):
        return (self.m.text(), self.n.text(), self.p.text())
