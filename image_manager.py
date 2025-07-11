##
# @file image_manager.py
# @brief Image handling and QLabel interaction abstraction for GUI-based applications.
#
# @details
# This module defines the @ref ImageManager class, which provides a structured way to
# manage source and result images in a PyQt5 GUI. All interactions with QLabel widgets are
# encapsulated, offering a reusable and testable interface.
#
# ### OOP Principles Applied:
# - **Encapsulation**: QLabel references and image path state are privately managed.
# - **Abstraction**: Complex GUI image logic is exposed through simplified, high-level methods.
#
# ### Responsibilities:
# - Load and display user-selected image in QLabel.
# - Safely clear QLabel contents with transparency.
# - Provide access to the currently loaded image path.
#
# @note This class is used by the AgriEdge image processing controller as the visual interface layer.
#
# @author Doğukan AVCI
# @date May 7, 2025
#

from PyQt5.QtWidgets import QFileDialog, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from os.path import basename
from skimage.io import imread

##
# @class ImageManager
# @brief Manages loading, clearing, and displaying images in QLabel widgets.
#
# @details
# This class centralizes all logic related to image display in the GUI. It abstracts away direct
# QLabel manipulation and integrates with PyQt5's `QFileDialog`, `QPixmap`, and optional `QStatusBar`
# for feedback messages.
#
# ### GUI Integration:
# - Sets size policies and smooth transformations for visual consistency.
# - Automatically propagates loaded image to both source and output areas.
#
# @see QLabel, QPixmap, QFileDialog
class ImageManager:
    def __init__(self, label_source, label_output, status_bar=None):
        """
        @brief Initializes the manager with GUI references.
        @param label_source QLabel to show the source image.
        @param label_output QLabel to show the result image.
        @param status_bar QStatusBar (optional) for status messages.
        """
        self.label_source = label_source
        self.label_output = label_output
        self.loaded_image = None
        self.status_bar = status_bar

    ##
    # @brief Opens a file dialog and loads the selected image.
    #
    # @details
    # After successful selection, the image is loaded into both `label_source` and `label_output`.
    # The source filename and size are also reflected in GUI fields if present in parent.
    #
    # @param parent QWidget: The parent widget (optional).
    #        Used for modal dialog behavior and to update additional GUI fields (e.g., `name_value`).
    #
    # @return str: Path to the loaded image file, or an empty string if cancelled or failed.
    #
    # @example
    # manager = ImageManager(label1, label2)
    # img_path = manager.open_image(self)
    def open_image(self, parent=None):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(parent, "Open Image File", "",
                                                  "Image Files (*.png *.jpg *.bmp)", options=options)
        if fileName:
            try:
                self.loaded_image = fileName
                self.label_source.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                pixmap = QPixmap(fileName)
                if pixmap.isNull():
                    raise ValueError("Görüntü yüklenemedi.")

                scaled_pixmap = pixmap.scaled(self.label_source.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_source.setPixmap(scaled_pixmap)
                self.label_output.setPixmap(scaled_pixmap)

                img = imread(fileName)
                name = basename(fileName)
                size = f"{img.shape[1]} x {img.shape[0]}"
                parent.name_value.setText(name)
                parent.size_value.setText(size)

                if parent and hasattr(parent, "applied_operations"):
                    parent.applied_operations.clear()

            except Exception as e:
                QMessageBox.critical(parent, "Yükleme Hatası", f"Görüntü yüklenemedi:\n{str(e)}")
                return ""
        return fileName

    ##
    # @brief Clears the contents of a QLabel using a transparent QPixmap.
    #
    # @details
    # This method is safe to call on any QLabel and also emits a feedback message
    # to the connected status bar if present.
    #
    # @param label QLabel: The label to be cleared.
    #
    # @note Sets the content to a transparent pixmap of the same size.
    def clear_label_safely(self, label):
        w = label.width()
        h = label.height()
        empty_pixmap = QPixmap(w, h)
        empty_pixmap.fill(Qt.transparent)
        label.setPixmap(empty_pixmap)
        label.setScaledContents(True)

        if self.status_bar:
            if label == self.label_source:
                self.status_bar.showMessage("Kaynak temizlendi \U0001F9F9", 2000)
            elif label == self.label_output:
                self.status_bar.showMessage("\u00C7ıktı temizlendi \U0001F9FC", 2000)

    ##
    # @brief Retrieves the file path of the currently loaded image.
    #
    # @return str: The path of the loaded image, or None if no image is loaded.
    #
    # @see open_image
    def get_loaded_image(self):
        return self.loaded_image
