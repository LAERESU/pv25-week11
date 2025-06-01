import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QDockWidget, QScrollArea, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class DataWargaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Warga CRUD Application")
        self.resize(850, 600)

        self.data = []
        self.editing_row = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        form_container = QWidget()
        scroll_area.setWidget(form_container)

        form_layout = QFormLayout(form_container)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        font_label = QFont("Segoe UI", 10)
        font_input = QFont("Segoe UI", 10)

        self.input_nama = QLineEdit()
        self.input_nama.setFont(font_input)
        self.input_ktp = QLineEdit()
        self.input_ktp.setFont(font_input)
        self.input_tempat_tgl = QLineEdit()
        self.input_tempat_tgl.setFont(font_input)
        self.input_alamat = QTextEdit()
        self.input_alamat.setFont(font_input)
        self.input_alamat.setFixedHeight(60)

        btn_paste_ktp = QPushButton("Paste KTP from Clipboard")
        btn_paste_ktp.setCursor(Qt.PointingHandCursor)
        btn_paste_ktp.clicked.connect(self.paste_ktp_clipboard)

        for label_text, widget in [
            ("Nama Lengkap:", self.input_nama),
            ("Nomor KTP:", self.input_ktp),
            ("Tempat, Tanggal Lahir:", self.input_tempat_tgl),
            ("Alamat:", self.input_alamat)
        ]:
            label = QLabel(label_text)
            label.setFont(font_label)
            form_layout.addRow(label, widget)

        form_layout.addRow(QLabel(""), btn_paste_ktp)

        btn_paste_alamat = QPushButton("Paste Alamat from Clipboard")
        btn_paste_alamat.setCursor(Qt.PointingHandCursor)
        btn_paste_alamat.clicked.connect(self.paste_alamat_clipboard)
        form_layout.addRow(QLabel(""), btn_paste_alamat)

        main_layout.addWidget(scroll_area)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_add = QPushButton("Tambah")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_record)
        self.btn_clear = QPushButton("Bersihkan")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_inputs)

        for btn in [self.btn_add, self.btn_clear]:
            btn.setMinimumWidth(90)
            btn.setFont(font_label)
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Nama Lengkap", "Nomor KTP", "Tempat, Tgl Lahir", "Alamat", "Aksi"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)

        self.dock = QDockWidget("Cari Data Warga", self)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        dock_widget = QWidget()
        dock_layout = QHBoxLayout(dock_widget)
        dock_layout.setContentsMargins(10, 10, 10, 10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama, KTP, tempat/tgl, alamat...")
        self.search_input.setFont(font_input)
        self.search_input.textChanged.connect(self.search_records)

        dock_layout.addWidget(self.search_input)
        self.dock.setWidget(dock_widget)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Yusril Ibtida Ramdhani | F1D022102")
        self.setStatusBar(self.status_bar)

    def paste_ktp_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.input_ktp.setText(text)

    def paste_alamat_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.input_alamat.setText(text)

    def add_record(self):
        nama = self.input_nama.text().strip()
        ktp = self.input_ktp.text().strip()
        tempat_tgl = self.input_tempat_tgl.text().strip()
        alamat = self.input_alamat.toPlainText().strip()

        if not nama or not ktp:
            QMessageBox.warning(self, "Peringatan", "Nama dan Nomor KTP harus diisi.")
            return

        self.data.append({
            "nama": nama,
            "ktp": ktp,
            "tempat_tgl": tempat_tgl,
            "alamat": alamat
        })
        self.refresh_table()
        self.clear_inputs()

    def refresh_table(self):
        self.table.setRowCount(0)
        for row_index, record in enumerate(self.data):
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(record["nama"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(record["ktp"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(record["tempat_tgl"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(record["alamat"]))

            # Buat widget tombol Edit dan Hapus di kolom Aksi
            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda _, r=row_index: self.load_selected_record(r))

            btn_delete = QPushButton("Hapus")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda _, r=row_index: self.delete_record_row(r))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.addStretch()

            self.table.setCellWidget(row_index, 4, action_widget)

        self.table.resizeColumnsToContents()

    def load_selected_record(self, row):
        record = self.data[row]
        self.input_nama.setText(record["nama"])
        self.input_ktp.setText(record["ktp"])
        self.input_tempat_tgl.setText(record["tempat_tgl"])
        self.input_alamat.setText(record["alamat"])

        self.editing_row = row
        self.btn_add.setEnabled(False)

        if not hasattr(self, 'btn_update_inline'):
            self.btn_update_inline = QPushButton("Update")
            self.btn_update_inline.setCursor(Qt.PointingHandCursor)
            self.btn_update_inline.setMinimumWidth(90)
            self.btn_update_inline.setFont(QFont("Segoe UI", 10))
            self.btn_update_inline.clicked.connect(self.update_record_inline)
            # Tambahkan tombol update ke layout tombol di bawah form
            self.centralWidget().layout().itemAt(1).addWidget(self.btn_update_inline)
        self.btn_update_inline.show()

    def update_record_inline(self):
        if self.editing_row is not None:
            row = self.editing_row
            nama = self.input_nama.text().strip()
            ktp = self.input_ktp.text().strip()
            tempat_tgl = self.input_tempat_tgl.text().strip()
            alamat = self.input_alamat.toPlainText().strip()

            if not nama or not ktp:
                QMessageBox.warning(self, "Peringatan", "Nama dan Nomor KTP harus diisi.")
                return

            self.data[row] = {
                "nama": nama,
                "ktp": ktp,
                "tempat_tgl": tempat_tgl,
                "alamat": alamat
            }
            self.refresh_table()
            self.clear_inputs()
            self.btn_add.setEnabled(True)
            self.btn_update_inline.hide()
            self.editing_row = None

    def delete_record_row(self, row):
        reply = QMessageBox.question(self, 'Konfirmasi', 'Yakin ingin menghapus data ini?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.data[row]
            self.refresh_table()
            self.clear_inputs()
            if hasattr(self, 'btn_update_inline'):
                self.btn_update_inline.hide()
            self.btn_add.setEnabled(True)
            self.editing_row = None

    def clear_inputs(self):
        self.input_nama.clear()
        self.input_ktp.clear()
        self.input_tempat_tgl.clear()
        self.input_alamat.clear()
        self.table.clearSelection()
        if hasattr(self, 'btn_update_inline'):
            self.btn_update_inline.hide()
        self.btn_add.setEnabled(True)
        self.editing_row = None

    def search_records(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            item_nama = self.table.item(row, 0).text().lower()
            item_ktp = self.table.item(row, 1).text().lower()
            item_tempat_tgl = self.table.item(row, 2).text().lower()
            item_alamat = self.table.item(row, 3).text().lower()

            match = (text in item_nama or text in item_ktp or
                     text in item_tempat_tgl or text in item_alamat)

            self.table.setRowHidden(row, not match)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataWargaApp()
    window.show()
    sys.exit(app.exec())
