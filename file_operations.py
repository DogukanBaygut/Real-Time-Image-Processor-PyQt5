##
# @file file_operations.py
# @brief GUI-integrated file saving, exporting, and exit management module.
#
# @details
# This module provides encapsulated file I/O operations for saving QLabel images to disk,
# exporting results, and safely exiting the PyQt5-based application.
#
# ### Object-Oriented Principles:
# - **Encapsulation**: All state variables (labels, parent, status bar) are managed with @ref property accessors.
# - **Abstraction**: Image saving logic is abstracted from GUI event handlers.
# - **Polymorphism**: Uses Qt's QFileDialog and QMessageBox uniformly across operations.
#
# ### Core Functionalities:
# - Save output directly or via dialog
# - Export source or output images with filename prompts
# - Exit with save confirmation
#
# @author Doğukan AVCI
# @date May 7, 2025
#

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication

##
# @class FileOperations
# @brief Encapsulates all image-related file operations for the GUI.
#
# @details
# This class provides a unified interface for saving, exporting, and closing the application
# while managing image data through QLabel widgets.
#
# @see QFileDialog, QMessageBox, QLabel, QStatusBar
#
# @note Frequently used by toolbar and menu action handlers in AgriEdge GUI.
class FileOperations:
    def __init__(self, parent, label_source, label_output, status_bar=None):
        """
        @brief Initializes the FileOperations handler with required widgets.
        @param parent QWidget: Parent window for modal dialogs and exit logic.
        @param label_source QLabel: Label for the original image.
        @param label_output QLabel: Label for the processed/output image.
        @param status_bar QStatusBar: Optional status bar for user feedback.
        """
        self._parent = parent
        self._label_source = label_source
        self._label_output = label_output
        self._status_bar = status_bar

    # ------------------- Encapsulated Properties -------------------

    ##
    # @property label_source
    # @brief Gets or sets the source QLabel.
    @property
    def label_source(self):
        return self._label_source

    @label_source.setter
    def label_source(self, value):
        self._label_source = value

    ##
    # @property label_output
    # @brief Gets or sets the output QLabel.
    @property
    def label_output(self):
        return self._label_output

    @label_output.setter
    def label_output(self, value):
        self._label_output = value

    ##
    # @property parent
    # @brief Gets or sets the main window.
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    ##
    # @property status_bar
    # @brief Gets or sets the optional status bar.
    @property
    def status_bar(self):
        return self._status_bar

    @status_bar.setter
    def status_bar(self, bar):
        self._status_bar = bar

    # ------------------- Core Functionalities -------------------

    ##
    # @brief Saves the output image to a default file path.
    #
    # @note This saves to "output_saved.png" without prompting.
    def save_output(self):
        if self.label_output.pixmap():
            self.label_output.pixmap().save("output_saved.png")
            self._show_status("Çıktı başarıyla kaydedildi 📀")

    ##
    # @brief Opens a dialog for saving the output image with a custom name.
    #
    # @note Supports PNG and JPG formats. Shows feedback in status bar.
    def save_output_as(self):
        if self.label_output.pixmap():
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent, "Save As Output", "", "PNG Files (*.png);;JPG Files (*.jpg)")
            if file_path:
                try:
                    if not self.label_output.pixmap().save(file_path):
                        raise IOError("Dosya kaydedilemedi.")
                    self._show_status("Çıktı farklı kaydedildi 📁")
                except Exception as e:
                    QMessageBox.critical(self.parent, "Kıyat Hatası", f"Dosya kaydedilirken hata oluştu:\n{str(e)}")

    ##
    # @brief Exports an image from a QLabel to disk via save dialog.
    #
    # @param label QLabel: The label containing the image to export.
    # @param title str: Dialog title and export context label.
    #
    # @example
    # ops.export_image(self.label_output, "Çıktı Dışa Aktar")
    def export_image(self, label, title):
        if label.pixmap():
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent, title, "", "PNG Files (*.png);;JPG Files (*.jpg)")
            if file_path:
                try:
                    if not label.pixmap().save(file_path):
                        raise IOError("Görsel kaydedilemedi.")
                    self._show_status(f"{title} tamamlandı 🖼")
                except Exception as e:
                    QMessageBox.critical(self.parent, "Kıyat Hatası", f"Kaydetme sırasında hata oluştu:\n{str(e)}")

    ##
    # @brief Prompts the user to optionally save output before exiting the app.
    #
    # @note Offers Yes/No/Cancel options. Cancels exit if requested.
    def exit_app(self):
        if self.label_output.pixmap():
            reply = QMessageBox.question(
                self.parent,
                "Uygulamadan Çık",
                "Çıkış yapmadan önce mevcut çıktıyı kaydetmek ister misiniz?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.save_output_as()
            elif reply == QMessageBox.Cancel:
                self._show_status("Çıkış iptal edildi ⛔")
                return
            else:
                self._show_status("Çıktı kaydedilmeden çıkılıyor 📂")

        self._show_status("Uygulama kapatılıyor... 👋")
        self.parent.close()

    ##
    # @brief Displays a message on the status bar, if available.
    #
    # @param message str: The message to display.
    # @param duration int: Duration in milliseconds (default = 3000 ms).
    def _show_status(self, message, duration=3000):
        if self._status_bar:
            self._status_bar.showMessage(message, duration)
