##
# @file conversion.py
# @brief Modular image conversion architecture using polymorphic design in PyQt5.
#
# @details
# This module implements a clean and extensible image conversion pipeline based on
# advanced Object-Oriented Programming (OOP) principles. It separates image conversion
# logic into abstract and concrete components, enabling easy expansion without breaking
# existing functionality.
#
# ### Key Concepts Demonstrated:
# - Abstraction via the @ref ImageOperation base class
# - Inheritance via @ref RGBToGray and @ref RGBToHSV subclasses
# - Polymorphism via dynamic dispatch of the `apply()` method
# - Encapsulation and data hiding via protected attributes
# - Undo support via internal state caching (`_prev_pixmap`)
#
# This file is part of the AgriEdge GUI framework.
#
# @author Doğukan AVCI
# @date May 6, 2025
#

from abc import ABC, abstractmethod
from skimage.io import imread
from skimage.color import rgb2gray, rgb2hsv, hsv2rgb
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

# =====================================================================
#                         ABSTRACT BASE CLASS
# =====================================================================

##
# @class ImageOperation
# @brief Abstract base class for all image conversion operations.
# @inherits ABC
#
# @details
# Defines a generic interface for image operations, enforcing the implementation
# of the `apply()` method via abstraction. It also supports an internal undo mechanism.
#
# ### OOP Principles:
# - **Abstraction**: Method `apply()` is declared as abstract.
# - **Encapsulation**: Attributes like `_image_path`, `_image_data` are protected.
# - **Data Hiding**: Undo functionality is only exposed through `undo()`.
#
# @note This class is not meant to be instantiated directly.
# @see RGBToGray, RGBToHSV
class ImageOperation(ABC):
    def __init__(self, image_path=None, label_output=None):
        """
        @brief Constructor
        @param image_path (str): Path to the image file.
        @param label_output (QLabel): Label to display processed image.
        """
        self._image_path = image_path
        self._image_data = imread(image_path) if image_path else None
        self._label_output = label_output
        self._prev_pixmap = None  # Used for GUI undo functionality

    def get_image_path(self):
        """
        @brief Getter for image path.
        @return str: Current image path.
        """
        return self._image_path

    def set_image_path(self, new_path):
        """
        @brief Setter that updates the image path and reloads image data.
        @param new_path (str): New file path for image.
        """
        self._image_path = new_path
        self._image_data = imread(new_path)

    @abstractmethod
    def apply(self):
        """
        @brief Abstract method that must be overridden by all subclasses.
        @return QPixmap: Converted image result.
        """
        pass

    def undo(self):
        """
        @brief Restores the last image shown before the current operation.
        @note Requires `_label_output` and `_prev_pixmap` to be set.
        """
        if self._label_output and self._prev_pixmap:
            self._label_output.setPixmap(self._prev_pixmap)
            self._label_output.setScaledContents(True)

# =====================================================================
#                         CONCRETE OPERATIONS
# =====================================================================

##
# @class RGBToGray
# @brief Converts an RGB image to Grayscale.
# @inherits ImageOperation
#
# @details
# Implements `apply()` method using skimage's `rgb2gray()` and displays
# the resulting grayscale image in a QLabel.
#
# ### Demonstrated Principles:
# - Inherits abstract interface from @ref ImageOperation
# - Runtime polymorphism via overridden `apply()`
# - Safe state manipulation via encapsulated image data
#
# @see ImageOperation
# @example
# handler = ConversionHandler(RGBToGray(path))
# handler.run()
class RGBToGray(ImageOperation):
    def apply(self):
        if self._image_data is not None and self._image_data.ndim == 3:
            if self._label_output:
                self._prev_pixmap = self._label_output.pixmap()

            rgb_img = self._image_data[:, :, :3]
            gray = rgb2gray(rgb_img)
            gray = (gray * 255).astype(np.uint8)
            h, w = gray.shape
            result = QPixmap.fromImage(QImage(gray.data, w, h, w, QImage.Format_Grayscale8))

            if self._label_output:
                self._label_output.setPixmap(result)
                self._label_output.setScaledContents(True)

            return result
        return None

##
# @class RGBToHSV
# @brief Converts an RGB image to HSV and amplifies hue visibility.
# @inherits ImageOperation
#
# @details
# Converts an RGB image to HSV, applies maximum saturation and brightness,
# and converts it back to RGB for visualization.
#
# ### Design Notes:
# - Ideal for visualizing color segmentation in high-contrast mode
# - Extends the @ref ImageOperation base with a specialized hue-focused operation
#
# @see ImageOperation
class RGBToHSV(ImageOperation):
    def apply(self):
        if self._image_data is not None and self._image_data.ndim == 3:
            if self._label_output:
                self._prev_pixmap = self._label_output.pixmap()

            rgb_img = self._image_data[:, :, :3]
            hsv = rgb2hsv(rgb_img)
            hsv[:, :, 1] = 1  # Full saturation
            hsv[:, :, 2] = 1  # Full brightness
            rgb_colored = (hsv2rgb(hsv) * 255).astype(np.uint8)
            h, w, _ = rgb_colored.shape
            result = QPixmap.fromImage(QImage(rgb_colored.data, w, h, 3 * w, QImage.Format_RGB888))

            if self._label_output:
                self._label_output.setPixmap(result)
                self._label_output.setScaledContents(True)

            return result
        return None

# =====================================================================
#                         OPERATION HANDLER
# =====================================================================

##
# @class ConversionHandler
# @brief Encapsulates and executes a given image conversion operation.
#
# @details
# A lightweight handler that enables operation chaining, reuse, and inversion of control
# by storing a reference to any @ref ImageOperation subclass. This allows flexible integration
# with multithreaded processing and undoable command patterns.
#
# ### OOP Concepts:
# - Polymorphism: Accepts any object that implements @ref ImageOperation
# - Data hiding: Operation details are abstracted behind `run()` and `undo()`
#
# @see ImageOperation
class ConversionHandler:
    def __init__(self, operation: ImageOperation):
        """
        @brief Constructor
        @param operation (ImageOperation): The image operation to execute.
        """
        self._operation = operation

    def set_operation(self, operation: ImageOperation):
        """
        @brief Dynamically replace the internal operation.
        @param operation (ImageOperation): New conversion strategy.
        """
        self._operation = operation

    def run(self):
        """
        @brief Executes the encapsulated operation.
        @return QPixmap: Processed image.
        """
        return self._operation.apply()

    def undo(self):
        """
        @brief Calls the undo mechanism of the encapsulated operation.
        """
        if self._operation:
            self._operation.undo()
