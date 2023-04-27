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

    def getInputs(self):
        return [float(i) for i in (self.x1.text(), self.y1.text(), self.z1.text())]