import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox,QGridLayout
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" photos edetor ")
        self.setGeometry(100, 100, 1000, 700)

        # create an interface 
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px solid #333; background-color: #f8f9fa;")

        self.open_btn = QPushButton("open photo")
        self.open_btn.clicked.connect(self.open_image)

        self.save_btn = QPushButton(" save photo")
        self.save_btn.clicked.connect(self.save_image)

        self.draw_btn = QPushButton("drow activate ")
        self.draw_btn.setCheckable(True)
        self.draw_btn.clicked.connect(self.toggle_drawing)

        self.clear_btn = QPushButton("remove preprocessing ")
        self.clear_btn.clicked.connect(self.clear_image)

        self.exit_btn = QPushButton("exit")
        self.exit_btn.clicked.connect(self.close_app)

        self.resize_btn = QPushButton("zoom in")
        self.resize_btn.clicked.connect(lambda: self.resize_image(1.5))

        self.resize_btn_smoler = QPushButton("zoom out")
        self.resize_btn_smoler.clicked.connect(lambda: self.resize_image_smoler(0.5))

# _______Filters Button
         
        self.filter_buttons = {
            "white and black": self.apply_grayscale,
            "increase sharpniss": self.apply_sharpen,
            "campiflage": self.apply_blur,
            "Hori Ref": self.apply_flip_horizontal,
            "Verti Ref": self.apply_flip_vertical
        }

        self.filter_layout = QVBoxLayout()
        self.filter_layout.addWidget(QLabel("Filters", self))
        for name, func in self.filter_buttons.items():
            btn = QPushButton(name)
            btn.clicked.connect(func)
            self.filter_layout.addWidget(btn)


      
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.exit_btn)
        control_layout.addWidget(self.open_btn)
        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(self.draw_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.resize_btn)
        control_layout.addWidget(self.resize_btn_smoler)


        main_layout = QGridLayout()
        main_layout.addLayout(self.filter_layout, 0, 0)
        main_layout.addWidget(self.label, 0, 1)
        main_layout.addLayout(control_layout, 1, 0, 1, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


        # design 
        self.setStyleSheet("""
            QMainWindow {
                background-color: #212529;
            }
            QLabel {
                font-size: 16px;
                color: #495057;
            }
            QPushButton {
                background-color: #8B0000;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003f7f;
            }
            QPushButton:checked {
                background-color: #28a745;
            }
        """)

        # variables to store img 
        self.image = None
        self.drawing_enabled = False
        self.last_point = None  
        self.original_image = None

    def toggle_drawing(self):
        self.drawing_enabled = not self.drawing_enabled
        self.draw_btn.setText("disable drawing" if self.drawing_enabled else "enable ")

    def open_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "choose a photo", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.image = cv2.imread(file_path)
            self.original_image = self.image.copy()  # save a copy
            self.display_image()

    def save_image(self):
        if self.image is not None:
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(self, "save the photo ", "", "Images (*.png *.jpg *.jpeg)", options=options)
            if save_path:
                cv2.imwrite(save_path, self.image)
                QMessageBox.information(self, "secess", "photo saved secessufuly ")
        else:
            QMessageBox.warning(self, "false", " there is no photo to be saved .")

    def clear_image(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.display_image()
        else:
            QMessageBox.warning(self, " false ", " there is no edits to be deleted .")

    def close_app(self):
        reply = QMessageBox.question(self, " sure ", " are you sure  to be out ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def display_image(self):
        if self.image is not None:
            height, width, channels = self.image.shape
            bytes_per_line = channels * width
            qt_image = QImage(self.image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qt_image)
            self.label.setPixmap(pixmap)
            self.label.setFixedSize(pixmap.size())

    def mousePressEvent(self, event):
        if self.drawing_enabled and self.image is not None and self.label.geometry().contains(event.pos()):
            x, y = self.get_image_coordinates(event.pos())
            self.last_point = (x, y)
            self.draw_point(x, y)

    def mouseMoveEvent(self, event):
        if self.drawing_enabled and self.image is not None and self.last_point:
            x, y = self.get_image_coordinates(event.pos())
            cv2.line(self.image, self.last_point, (x, y), (0, 0, 255), 2)
            self.last_point = (x, y)
            self.display_image()

    def mouseReleaseEvent(self, event):
        if self.drawing_enabled:
            self.last_point = None

    def get_image_coordinates(self, pos):
        """ convert mouse coordinate to photo coordinate """
        label_rect = self.label.geometry()
        x_ratio = self.image.shape[1] / self.label.width()
        y_ratio = self.image.shape[0] / self.label.height()

        x = int((pos.x() - label_rect.x()) * x_ratio)
        y = int((pos.y() - label_rect.y()) * y_ratio)
        return max(0, min(x, self.image.shape[1] - 1)), max(0, min(y, self.image.shape[0] - 1))

    def draw_point(self, x, y):
        """ draw a point in a photo """
        cv2.circle(self.image, (x, y), 3, (0, 0, 255), -1)
        self.display_image()
# __________________________________________________________________________Filters
    def apply_grayscale(self):
        if self.image is not None:
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
            self.display_image()

    def apply_sharpen(self):
        if self.image is not None:
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            self.image = cv2.filter2D(self.image, -1, kernel)
            self.display_image()

    def apply_blur(self):
        if self.image is not None:
            self.image = cv2.GaussianBlur(self.image, (15, 15), 0)
            self.display_image()

    def apply_flip_horizontal(self):
        if self.image is not None:
            self.image = cv2.flip(self.image, 1)
            self.display_image()

    def apply_flip_vertical(self):
        if self.image is not None:
            self.image = cv2.flip(self.image, 0)
            self.display_image()

    def resize_image(self, scale):
        if self.image is not None:
            height, width = self.image.shape[:2]
            new_size = (int(width * scale), int(height * scale))
            self.image = cv2.resize(self.image, new_size)
            self.display_image()
    def resize_image_smoler(self, scale):
        if self.image is not None:
            height, width = self.image.shape[:2]
            new_size = (int(width * scale), int(height * scale))
            self.image = cv2.resize(self.image, new_size)
            self.display_image()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())