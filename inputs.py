from PyQt5.QtWidgets import QLineEdit, QDialog, QDialogButtonBox, QFormLayout

class SphereDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.x1 = QLineEdit(self)
        self.y1 = QLineEdit(self)
        self.z1 = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow("X1", self.x1)
        layout.addRow("Y1", self.y1)
        layout.addRow("Z1", self.z1)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.x1.text(), self.y1.text(), self.z1.text())
    

class LineDialog(QDialog):
    def __init__(self, number, parent=None):
        super().__init__(parent)

        self.x1 = QLineEdit(self)
        self.y1 = QLineEdit(self)
        self.z1 = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        layout.addRow(f"X{number}", self.x1)
        layout.addRow(f"Y{number}", self.y1)
        layout.addRow(f"Z{number}", self.z1)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return (self.x1.text(), self.y1.text(), self.z1.text())