# -*- coding: utf-8 -*-
"""
===============================================================================
        ADVANCED IMAGE PROCESSING INTERFACE - OOP2 LAB FINAL PROJECT
===============================================================================

Author  : Doğukan Avcı
Date    : April 27, 2025
Course  : Object-Oriented Programming II (Spring 2024-2025)

Description:
------------
This is the main controller script for a modular, object-oriented GUI-based
image processing application developed using PyQt5. The project aims to demonstrate
principles of object-oriented design including abstraction, inheritance, and
polymorphism while utilizing key Python libraries such as `scikit-image`, `numpy`,
and `PyQt5`.

Key Features:
-------------
- Dynamic GUI layout with Qt Designer integration.
- Modular architecture for conversion, segmentation, and edge detection operations.
- Reversible action history with undo/redo using polymorphic command structure.
- Support for grayscale and HSV conversion, three segmentation algorithms, and
  four edge detection techniques.
- Real-time threshold adjustment with slider-based control.
- Smart UI state management and tooltip/icon feedback for all actions.
- Enhanced usability through progress tracking and fade-in visual effects.

Modules:
--------
- `conversion.py`           : Contains grayscale and HSV conversion operations.
- `segmentation.py`         : Implements Multi-Otsu, Chan-Vese, and Morphological Snakes.
- `edge_detection.py`       : Supports Roberts, Sobel, Scharr, Prewitt detectors.
- `image_manager.py`        : Manages image loading, clearing, and displaying.
- `file_operations.py`      : Handles image saving/exporting and exit operations.
- `ui_effects.py`           : Visual effects such as hover animations and fade-in.
- `processing_worker.py`    : Multithreaded execution of time-intensive operations.
- `ui_state_manager.py`     : Controls widget availability and UI state logic.

How to Run:
-----------
Execute the module directly with Python 3.x. Ensure all modules and `style.qss`
are present in the working directory.

    python main.py

"""

# ============================================================================
#                            IMPORT STATEMENTS
# ============================================================================

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

import sys
import time
import os

# UI and logic layer imports
from LabFinal import Ui_MainWindow
from conversion import RGBToGray, RGBToHSV, ConversionHandler
from segmentation import MultiOtsuSegmentation, ChanVeseSegmentation, MorphologicalSnakesSegmentation, SegmentationHandler
from edge_detection import RobertsEdge, SobelEdge, ScharrEdge, PrewittEdge, EdgeDetectionHandler
from image_manager import ImageManager
from file_operations import FileOperations
from ui_effects import fade_in_widget, animate_button_hover
from processing_worker import ProcessingThread
from ui_state_manager import StandardUIStateManager


# ============================================================================
#                            MAIN WINDOW CLASS
# ============================================================================

##
# @class MainWindow
# @brief Main controller window for the Advanced Image Processing Interface.
#
# This class acts as the central hub connecting the PyQt5 UI (generated via Qt Designer)
# with the backend logic for image processing. It handles loading, displaying, processing,
# and exporting images, while also managing UI state, history tracking, and user interaction.
#
# @details
# - Inherits from both QMainWindow and Ui_MainWindow.
# - Initializes all UI widgets, icons, signals, and slots.
# - Supports conversion (RGB to Grayscale/HSV), segmentation, edge detection, undo/redo.
# - Uses threading (via ProcessingThread) to keep GUI responsive during operations.
#
# @author Doğukan Avcı
# @date April 27, 2025
#
# @see conversion.py, segmentation.py, edge_detection.py, image_manager.py, etc.
# @see ProcessingThread, StandardUIStateManager
#

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The MainWindow class defines the core user interface and connects UI components
    with image processing logic. It integrates various modules to enable operations
    like image conversion, segmentation, edge detection, file handling, and state
    management.

    Inherits:
        QMainWindow: Base class for all main windows in PyQt5.
        Ui_MainWindow: Auto-generated UI class from Qt Designer.
    """
    
    def __init__(self):
        """
        Initializes the main application window, sets up UI bindings, 
        and prepares all processing handlers and GUI components.
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        from ui_effects import animate_button_hover  # Redundant import, kept for clarity
        self.progressBar.setValue(0)

        # Define processing buttons and map them to their corresponding operation names
        self.processing_buttons = {
            self.GrayScale_button: "grayscale",
            self.HSV_button: "hsv",
            self.multiotsu_Button: "multiotsu",
            self.chanvese_Buttton: "chanvese",
            self.morp_button: "morphsnake",
            self.Roberts_button: "roberts",
            self.Sobel_button: "sobel",
            self.Scharr_button: "scharr",
            self.Prewitt_button: "prewitt"
        }

        # Connect buttons with corresponding handlers including hover animation
        for button, process_name in self.processing_buttons.items():
            button.clicked.connect(lambda _, b=button, p=process_name: [animate_button_hover(b), self.apply_processing(p)])

        
        # ============================================================================
        #                    INITIAL UI LAYOUT AND COMPONENT SETUP
        # ============================================================================

        # Set window size relative to screen dimensions
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry()
        self.resize(int(size.width() * 0.7), int(size.height() * 0.7))

        # Configure source and output labels
        self.label_source.setText("📂 Lütfen bir görüntü açın")
        self.label_source.setAlignment(Qt.AlignCenter)
        self.label_output.setText("📤 İşlem sonucu burada görünecek")
        self.label_output.setAlignment(Qt.AlignCenter)
        self.label_source.setStyleSheet("font-size: 16pt; font-weight: bold; color: #555;")
        self.label_output.setStyleSheet("font-size: 16pt; font-weight: bold; color: #555;")

        self.label_source.setScaledContents(True)
        self.label_output.setScaledContents(True)
        
        

        # Conversion butonları
        self.GrayScale_button.setIcon(QIcon("icons/gray.png"))
        self.HSV_button.setIcon(QIcon("icons/hue.png"))
        
        # Source butonları
        self.Source_Open_Button.setIcon(QIcon("icons/open.png"))
        self.Source_Clear_button.setIcon(QIcon("icons/clear.png"))
        self.Source_Export_button.setIcon(QIcon("icons/export.png"))
        
        # Segmentation butonları
        self.multiotsu_Button.setIcon(QIcon("icons/multiotsu.png"))
        self.chanvese_Buttton.setIcon(QIcon("icons/chanvese.png"))
        self.morp_button.setIcon(QIcon("icons/morph.png"))
        
        # Edge Detection butonları
        self.Roberts_button.setIcon(QIcon("icons/roberts.png"))
        self.Sobel_button.setIcon(QIcon("icons/sobel.png"))
        self.Scharr_button.setIcon(QIcon("icons/scharr.png"))
        self.Prewitt_button.setIcon(QIcon("icons/prewitt.png"))
        
        # Output butonları
        self.Undo_Output_button.setIcon(QIcon("icons/undo.png"))
        self.Redo_Output_button.setIcon(QIcon("icons/redo.png"))
        self.Clear_Output_button.setIcon(QIcon("icons/clear.png"))
        self.Save_Output_button.setIcon(QIcon("icons/save.png"))
        self.Save_as_Output_button.setIcon(QIcon("icons/saveas.png"))
        self.Export_Output_button.setIcon(QIcon("icons/export.png"))

        # Initialize history tracking
        self.operation_history = []
        self.history_index = -1
        self.applied_operations = set()
        self.image_operations = {}  # Dictionary to track operations per file

        # ============================================================================
        #                          MENU ICON ASSIGNMENTS
        # ============================================================================

        self.actionOpen_Source.setIcon(QIcon("icons/open.png"))
        self.actionSave_Output.setIcon(QIcon("icons/save.png"))
        self.actionSave_As_Output.setIcon(QIcon("icons/save.png"))
        self.actionOutput.setIcon(QIcon("icons/export.png"))
        self.actionSource.setIcon(QIcon("icons/export.png"))
        self.actionExit_Shift_F4.setIcon(QIcon("icons/close.png"))
        self.actionRGB_to_Grayscale.setIcon(QIcon("icons/gray.png"))
        self.actionRGB_to_HSV.setIcon(QIcon("icons/hue.png"))
        self.actionUndo_Output.setIcon(QIcon("icons/undo.png"))
        self.actionRedo_Output.setIcon(QIcon("icons/redo.png"))
        self.clearSource_Button_menu.setIcon(QIcon("icons/clear.png"))
        self.clearOutput_Button_menu.setIcon(QIcon("icons/clear.png"))

        default_icon = QIcon("icons/default.png")

        # Assign default icons to operations not having specific icons
        self.actionRoberts.setIcon(default_icon)
        self.actionSobel.setIcon(default_icon)
        self.actionScharr.setIcon(default_icon)
        self.actionPrewitt.setIcon(default_icon)
        self.actionMulti_Otsu_Thresholding.setIcon(default_icon)
        self.actionChan_Vese_Segmentation.setIcon(default_icon)
        self.actionMorphological_Snakes.setIcon(default_icon)

        # ============================================================================
        #                          MODULE INITIALIZATIONS
        # ============================================================================

        self.ui_manager = StandardUIStateManager(self)
        self.ui_manager.disable_all()

        self.manager = ImageManager(self.label_source, self.label_output, self.statusBar())
        self.file_ops = FileOperations(self, self.label_source, self.label_output, self.statusBar())

        # ============================================================================
        #                      SIGNAL-SLOT CONNECTIONS (ACTIONS)
        # ============================================================================

        self.actionOpen_Source.triggered.connect(lambda: [self.manager.open_image(self), self.ui_manager.enable_after_image_loaded()])
        self.clearSource_Button_menu.triggered.connect(lambda: self.manager.clear_label_safely(self.label_source))
        self.clearOutput_Button_menu.triggered.connect(lambda: self.manager.clear_label_safely(self.label_output))
        self.actionRGB_to_Grayscale.triggered.connect(lambda: self.apply_processing("grayscale"))
        self.actionRGB_to_HSV.triggered.connect(lambda: self.apply_processing("hsv"))
        self.actionMulti_Otsu_Thresholding.triggered.connect(lambda: self.apply_processing("multiotsu"))
        self.actionChan_Vese_Segmentation.triggered.connect(lambda: self.apply_processing("chanvese"))
        self.actionMorphological_Snakes.triggered.connect(lambda: self.apply_processing("morphsnake"))
        self.actionRoberts.triggered.connect(lambda: self.apply_processing("roberts"))
        self.actionSobel.triggered.connect(lambda: self.apply_processing("sobel"))
        self.actionScharr.triggered.connect(lambda: self.apply_processing("scharr"))
        self.actionPrewitt.triggered.connect(lambda: self.apply_processing("prewitt"))
        self.actionSave_Output.triggered.connect(self.file_ops.save_output)
        self.actionSave_As_Output.triggered.connect(self.file_ops.save_output_as)
        self.actionSource.triggered.connect(lambda: self.file_ops.export_image(self.label_source, "Export Source"))
        self.actionOutput.triggered.connect(lambda: self.file_ops.export_image(self.label_output, "Export Output"))
        self.actionExit_Shift_F4.triggered.connect(self.file_ops.exit_app)

        # ============================================================================
        #                      SIGNAL-SLOT CONNECTIONS (BUTTONS)
        # ============================================================================

        self.Clear_Output_button.clicked.connect(lambda: self.manager.clear_label_safely(self.label_output))
        self.Export_Output_button.clicked.connect(lambda: self.file_ops.export_image(self.label_output, "Export Output"))
        self.Redo_Output_button.clicked.connect(self.redo_last_operation)
        self.Undo_Output_button.clicked.connect(self.undo_last_operation)
        self.Save_Output_button.clicked.connect(self.file_ops.save_output)
        self.Save_as_Output_button.clicked.connect(self.file_ops.save_output_as)
        self.Source_Open_Button.clicked.connect(lambda: [self.manager.open_image(self), self.ui_manager.enable_after_image_loaded()])
        self.Source_Clear_button.clicked.connect(lambda: self.manager.clear_label_safely(self.label_source))
        self.Source_Export_button.clicked.connect(lambda: self.file_ops.export_image(self.label_source, "Export Source"))

        # ============================================================================
        #                             THRESHOLD SLIDER
        # ============================================================================

        self.th_horizontalSlider.setMinimum(0)
        self.th_horizontalSlider.setMaximum(255)
        self.th_horizontalSlider.setValue(100)
        self.th_horizontalSlider.setTickInterval(5)
        self.th_horizontalSlider.valueChanged.connect(self.on_threshold_changed)

        # Apply custom stylesheet
        self.apply_styles()


        # Apply custom stylesheet from external QSS file
    def apply_styles(self):
        """
        Loads and applies the custom Qt Style Sheet (QSS) to the main window.
        Ensures consistent UI theming across all widgets.
        """
        with open("style.qss", "r") as f:
            self.setStyleSheet(f.read())


        # ============================================================================
        #                       MAIN PROCESSING DISPATCHER METHOD
        # ============================================================================

    def apply_processing(self, operation_type: str, threshold=None):
        """
        Dispatches and manages the application of an image processing operation.

        Based on the selected `operation_type`, this method:
        - Initializes the corresponding processing object
        - Creates a threaded handler for async processing
        - Tracks the operation in history for undo/redo support
        - Prevents duplicate operations where needed

        Args:
            operation_type (str): Type of operation to apply
            One of: 'grayscale', 'hsv', 'multiotsu', 'chanvese', 'morphsnake',
            'roberts', 'sobel', 'scharr', 'prewitt'
            threshold (int, optional): Threshold value for edge operations.
        """
        image_path = self.manager.get_loaded_image()
        if not image_path:
            return

        edge_ops = {"sobel", "scharr", "prewitt", "roberts"}

        # Prevent redundant non-edge operations
        if operation_type not in edge_ops and operation_type in self.applied_operations:
            QMessageBox.information(self, "Bilgi", f"'{operation_type}' işlemi zaten uygulanmış.")
            self.statusbar.showMessage(f"'{operation_type}' işlemi zaten uygulanmış!", 5000)
            return

        # Save current edge operation for live threshold adjustment
        self.last_edge_operation = operation_type if operation_type in edge_ops else None

        if threshold is None:
            threshold = self.th_horizontalSlider.value()

            # Map operation to factory and handler class
        operation_map = {
                "grayscale": (lambda: RGBToGray(image_path), ConversionHandler),
                "hsv": (lambda: RGBToHSV(image_path), ConversionHandler),
                "multiotsu": (lambda: MultiOtsuSegmentation(image_path), SegmentationHandler),
                "chanvese": (lambda: ChanVeseSegmentation(image_path), SegmentationHandler),
                "morphsnake": (lambda: MorphologicalSnakesSegmentation(image_path), SegmentationHandler),
                "roberts": (lambda: RobertsEdge(image_path, threshold), EdgeDetectionHandler),
                "sobel": (lambda: SobelEdge(image_path, threshold), EdgeDetectionHandler),
                "scharr": (lambda: ScharrEdge(image_path, threshold), EdgeDetectionHandler),
                "prewitt": (lambda: PrewittEdge(image_path, threshold), EdgeDetectionHandler)
            }

        op_factory, handler_class = operation_map.get(operation_type, (None, None))
        if op_factory and handler_class:
            self.progressBar.setValue(0)
            self.thread = ProcessingThread(op_factory(), handler_class, image_path, operation_type)
            self.thread.progress.connect(self.progressBar.setValue)
            self.thread.result_ready.connect(self.handle_processing_result)

            # Register operation to prevent re-execution
            if operation_type not in edge_ops:
                self.applied_operations.add(operation_type)

            # Track applied operations per image
            filename = os.path.basename(image_path)
            if filename not in self.image_operations:
                self.image_operations[filename] = []
            if operation_type not in self.image_operations[filename]:
                self.image_operations[filename].append(operation_type)

            # Append operation to history stack
            if self.history_index + 1 < len(self.operation_history):
                self.operation_history = self.operation_history[:self.history_index + 1]
            self.operation_history.append((operation_type, image_path, threshold))
            self.history_index += 1

            print(f"'{filename}' için uygulanan işlemler: {self.image_operations[filename]}")
            self.thread.start()


            
        # ============================================================================
        #                  SLOT: HANDLE PROCESSING RESULT FROM THREAD
        # ============================================================================

    def handle_processing_result(self, result_pixmap, duration, operation_type):
        """
        Receives the result of an image processing operation from a background thread.
        Scales and displays the resulting image in the output label, with visual feedback.

        Args:
            result_pixmap (QPixmap): The processed image.
            duration (float): Processing time in seconds (optional, for profiling).
            operation_type (str): The operation performed.
        """
        if isinstance(result_pixmap, QPixmap):
            self.label_output.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            scaled_result = result_pixmap.scaled(self.label_output.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_output.setPixmap(scaled_result)
            self.label_output.setScaledContents(False)

            fade_in_widget(self.label_output)
            self.statusBar().showMessage(f"{operation_type.upper()} işlemi başarıyla uygulandı. ✅🎯", 3000)
            self.ui_manager.enable_after_processing()


        # ============================================================================
        #                SLOT: THRESHOLD SLIDER CHANGED (REAL-TIME UPDATE)
        # ============================================================================

    def on_threshold_changed(self, value):
        """
        Handles threshold slider updates. Re-triggers the last edge operation 
        with the new threshold value in real-time.

        Args:
                value (int): New threshold value selected by the user.
        """
        self.th_label.setText(f"Threshold: {value}")
        if self.last_edge_operation in ["sobel", "scharr", "prewitt", "roberts"]:
            self.apply_processing(self.last_edge_operation, threshold=value)


        # ============================================================================
        #                          IMAGE HISTORY STACK HANDLER
        # ============================================================================

    def add_to_history(self):
        """
        Captures the current output image state and appends it to a history buffer.
        Enables pixel-perfect undo/redo functionality via QImage cloning.
        """
        if self.label_output.pixmap():
            qimg = self.label_output.pixmap().toImage()
            if not hasattr(self, "history"):
                self.history = []
                self.history_index = -1
            self.history = self.history[:self.history_index + 1]
            self.history.append(qimg.copy())
            self.history_index += 1

        # ============================================================================
        #                           WINDOW CLOSE HANDLER
        # ============================================================================

    def closeEvent(self, event):
        """
        Intercepts window close event and optionally saves the output image
        if present. Prompts the user with a confirmation dialog.

        Args:
            event (QCloseEvent): Event object provided by Qt framework.
        """
        if self.label_output.pixmap():
            reply = QMessageBox.question(
                self,
                "Çıkmadan Önce",
                "Çıktı kaydedilsin mi?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )

            if reply == QMessageBox.Yes:
                try:
                    self.label_output.pixmap().save("output_saved_on_exit.png")
                except Exception as e:
                    QMessageBox.critical(self, "Kayıt Hatası", f"Kaydetme başarısız oldu:\n{str(e)}")
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


        # ============================================================================
        #                     INTERNAL IMAGE OPERATION RE-RUNNER
        # ============================================================================

    def _run_operation(self, operation_type, image_path, threshold=None, record_history=True):
        """
        Internal method used by undo/redo system to re-execute a previous
        image processing operation with exact parameters.

        Args:
            operation_type (str): Operation to apply.
            image_path (str): Path to the original image.
            threshold (int, optional): Threshold value (for edge detectors).
            record_history (bool): If False, operation is not added to history again.
        """
        operation_map = {
                "grayscale": (lambda: RGBToGray(image_path), ConversionHandler),
                "hsv": (lambda: RGBToHSV(image_path), ConversionHandler),
                "multiotsu": (lambda: MultiOtsuSegmentation(image_path), SegmentationHandler),
                "chanvese": (lambda: ChanVeseSegmentation(image_path), SegmentationHandler),
                "morphsnake": (lambda: MorphologicalSnakesSegmentation(image_path), SegmentationHandler),
                "roberts": (lambda: RobertsEdge(image_path, threshold), EdgeDetectionHandler),
                "sobel": (lambda: SobelEdge(image_path, threshold), EdgeDetectionHandler),
                "scharr": (lambda: ScharrEdge(image_path, threshold), EdgeDetectionHandler),
                "prewitt": (lambda: PrewittEdge(image_path, threshold), EdgeDetectionHandler)
            }

        op_factory, handler_class = operation_map.get(operation_type, (None, None))
        if op_factory and handler_class:
            handler = handler_class(op_factory())
            result_pixmap = handler.run()

            if isinstance(result_pixmap, QPixmap):
                scaled_result = result_pixmap.scaled(self.label_output.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_output.setPixmap(scaled_result)
                self.label_output.setScaledContents(False)
                fade_in_widget(self.label_output)
                self.ui_manager.enable_after_processing()

                if record_history:
                    self.operation_history = self.operation_history[:self.history_index + 1]
                    self.operation_history.append((operation_type, image_path, threshold))
                    self.history_index += 1
                    self.add_to_history()


    # ============================================================================
    #                         UNDO / REDO OPERATION SUPPORT
    # ============================================================================

    def undo_last_operation(self):
        """
        Reverts the last applied operation by stepping one position back
        in the operation history stack and executing the previous action.
        """
        if not hasattr(self, "operation_history") or self.history_index <= 0:
            self.statusBar().showMessage("Geri alınacak işlem yok ⛔", 3000)
            return

        self.history_index -= 1
        op_type, img_path, threshold = self.operation_history[self.history_index]
        self._run_operation(op_type, img_path, threshold, record_history=False)
        self.statusBar().showMessage(f"{op_type.upper()} geri alındı ↩️", 3000)


    def redo_last_operation(self):
        """
        Re-applies the next operation in the operation history if available,
        effectively redoing the previously undone action.
        """
        if self.history_index + 1 < len(self.operation_history):
            self.history_index += 1
            op_type, img_path, threshold = self.operation_history[self.history_index]
            self._run_operation(op_type, img_path, threshold, record_history=False)
            self.statusBar().showMessage(f"{op_type} tekrar uygulandı 🔁", 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.availableGeometry()
    window = MainWindow()
    window.resize(int(size.width() * 0.7), int(size.height() * 0.7))
    window.show()
    sys.exit(app.exec_())
