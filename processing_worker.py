##
# @file processing_worker.py
# @brief Background image processing thread for responsive PyQt5 GUI.
#
# @details
# This module defines the @ref ProcessingThread class, a QThread subclass that offloads
# heavy image processing operations from the main GUI thread. It ensures responsiveness
# in the application by allowing processing to run asynchronously, emitting signals for
# progress and result delivery.
#
# ### OOP Features:
# - **Encapsulation**: Thread logic and handler interaction are enclosed in the thread class.
# - **Abstraction**: Handler class abstracts the image processing logic from threading.
# - **Polymorphism**: Supports multiple types of operations via generic handler design.
# - **Multithreading**: Improves responsiveness by avoiding GUI freezes.
#
# ### Signal Design:
# - `progress` emits percentage progress.
# - `result_ready` emits final result, time taken, and operation label.
#
# @author Doğukan AVCI
# @date May 7, 2025
#

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox
import time

##
# @class ProcessingThread
# @brief Executes image processing operations in a separate thread.
# @inherits QThread
#
# @details
# Used to process visual tasks (e.g., filtering, segmentation) without freezing the UI.
# Integrates a polymorphic handler to support different operation types such as
# `ConversionHandler`, `SegmentationHandler`, etc.
#
# @note Signals are emitted to communicate progress and final result to the main thread.
#
# @see QThread, pyqtSignal
class ProcessingThread(QThread):
    ##
    # @var progress
    # @brief Signal emitting integer percentage updates (0–100).
    progress = pyqtSignal(int)

    ##
    # @var result_ready
    # @brief Signal emitting QPixmap result, float duration (in seconds), and operation name (str).
    result_ready = pyqtSignal(QPixmap, float, str)

    def __init__(self, operation, handler_class, image_path, op_name):
        """
        @brief Initializes the thread with a handler class and operation.
        @param operation Object: Instance of image operation (e.g., RGBToGray, SobelEdge).
        @param handler_class type: Class that wraps the operation (e.g., ConversionHandler).
        @param image_path str: Path of the image to be processed.
        @param op_name str: Human-readable name of the operation for GUI display.
        """
        super().__init__()
        self.operation = operation
        self.handler_class = handler_class
        self.image_path = image_path
        self.op_name = op_name

    ##
    # @brief Thread entry point for running image processing.
    #
    # @details
    # This function is executed when `.start()` is called on the thread object.
    # It simulates progress, executes the handler logic, measures time,
    # and emits `result_ready` when complete.
    #
    # @warning Any exceptions raised during processing are caught and shown to user via QMessageBox.
    def run(self):
        start_time = time.time()
        self.progress.emit(20)
        time.sleep(0.1)  # Simulate pre-processing

        try:
            handler = self.handler_class(self.operation)
            result = handler.run()
        except Exception as e:
            QMessageBox.critical(None, "İşlem Hatası", f"İşlem uygulanırken bir hata oluştu:\n{str(e)}")
            return

        self.progress.emit(60)
        time.sleep(0.1)  # Simulate post-processing

        end_time = time.time()
        duration = end_time - start_time

        self.progress.emit(100)
        self.result_ready.emit(result, duration, self.op_name)
