##
# @file edge_detection.py
# @brief Polymorphic and threshold-aware edge detection module with GUI integration.
#
# @details
# This module provides a class hierarchy for edge detection using Python's OOP capabilities.
# It supports four classic filters: Sobel, Roberts, Scharr, and Prewitt.
#
# ### Object-Oriented Features:
# - **Abstraction**: Common interface via @ref AbstractEdgeDetector.
# - **Inheritance**: Concrete detectors (e.g. @ref SobelEdge) extend the abstract base.
# - **Polymorphism**: Uniform call to `detect()` across all edge types.
# - **Encapsulation**: Threshold, label, and image state protected with `_` and accessed through methods.
# - **Data Hiding**: Internal QPixmap and image loading are not directly exposed.
#
# ### Features:
# - PyQt5-compatible QLabel updates.
# - Undoable GUI feedback via cached `QPixmap`.
# - Runtime threshold adjustment.
#
# @date May 6, 2025
# @author Doğukan AVCI
#

from abc import ABC, abstractmethod
from PyQt5.QtGui import QPixmap, QImage
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.filters import roberts, sobel, scharr, prewitt
import numpy as np

# =====================================================================
#                      ABSTRACT BASE CLASS
# =====================================================================

##
# @class AbstractEdgeDetector
# @brief Abstract base class for all edge detection operations.
# @inherits ABC
#
# @details
# This abstract base class provides threshold support, undo logic,
# and image conversion utilities. Subclasses must implement `detect()`.
#
# ### Encapsulated State:
# - `_image_path` (str): Input image path
# - `_threshold` (int): Threshold level [0–255]
# - `_label_output` (QLabel): Output label in the GUI
# - `_prev_pixmap` (QPixmap): Cache for undo
#
# @note This class should not be instantiated directly.
# @see SobelEdge, ScharrEdge, RobertsEdge, PrewittEdge
class AbstractEdgeDetector(ABC):
    def __init__(self, image_path, threshold=None, label_output=None):
        """
        @brief Initializes internal state and GUI target.
        @param image_path Path to the image.
        @param threshold Threshold value (0–255).
        @param label_output QLabel for GUI display (optional).
        """
        self._image_path = image_path
        self._threshold = threshold
        self._label_output = label_output
        self._prev_pixmap = None

    def _apply_threshold(self, edge_image):
        """
        @brief Applies thresholding if a threshold is set.
        @param edge_image (ndarray): Float image in range [0,1]
        @return ndarray: Binary or unmodified image
        """
        if self._threshold is None:
            return edge_image
        return edge_image > (self._threshold / 255.0)

    def set_threshold(self, value):
        """@brief Dynamically sets the threshold value."""
        self._threshold = value

    def get_image_path(self):
        """@brief Returns the current image file path."""
        return self._image_path

    def set_image_path(self, path):
        """@brief Sets a new image path."""
        self._image_path = path

    @abstractmethod
    def detect(self):
        """
        @brief Abstract method that must be overridden by concrete detectors.
        @return QPixmap: Output image with detected edges.
        """
        pass

    def undo(self):
        """
        @brief Restores previous image result from `QPixmap`.
        @note GUI safety mechanism to allow undo operations.
        """
        if self._label_output and self._prev_pixmap:
            self._label_output.setPixmap(self._prev_pixmap)
            self._label_output.setScaledContents(True)

    def _load_gray_image(self):
        """
        @brief Loads the image from disk and converts it to grayscale if needed.
        @return ndarray: Grayscale image
        """
        img = imread(self._image_path)
        if img.ndim == 3:
            if img.shape[2] == 4:
                img = img[:, :, :3]
            img = rgb2gray(img)
        return img

    def _to_pixmap(self, edge_image):
        """
        @brief Converts a 2D image to a QPixmap for GUI display.
        @param edge_image ndarray: Input edge map in [0,1] or binary
        @return QPixmap: Display-ready image
        """
        output_img = (edge_image * 255).astype(np.uint8)
        h, w = output_img.shape
        qimg = QImage(output_img.data, w, h, w, QImage.Format_Grayscale8)
        return QPixmap.fromImage(qimg)


# =====================================================================
#                   CONCRETE EDGE DETECTION CLASSES
# =====================================================================

##
# @class SobelEdge
# @brief Performs Sobel edge detection.
# @inherits AbstractEdgeDetector
#
# @details
# Computes intensity gradient using Sobel operator. 
# Good for horizontal/vertical edge sensitivity.
#
# @see AbstractEdgeDetector
class SobelEdge(AbstractEdgeDetector):
    def detect(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()
        edge = sobel(self._load_gray_image())
        edge = self._apply_threshold(edge)
        result = self._to_pixmap(edge)
        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)
        return result

##
# @class RobertsEdge
# @brief Performs Roberts cross edge detection.
# @inherits AbstractEdgeDetector
#
# @details
# Computes diagonal edges. Very sensitive and fast.
#
# @see AbstractEdgeDetector
class RobertsEdge(AbstractEdgeDetector):
    def detect(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()
        edge = roberts(self._load_gray_image())
        edge = self._apply_threshold(edge)
        result = self._to_pixmap(edge)
        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)
        return result

##
# @class ScharrEdge
# @brief Performs Scharr edge detection.
# @inherits AbstractEdgeDetector
#
# @details
# High-accuracy alternative to Sobel with better rotational symmetry.
#
# @see AbstractEdgeDetector
class ScharrEdge(AbstractEdgeDetector):
    def detect(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()
        edge = scharr(self._load_gray_image())
        edge = self._apply_threshold(edge)
        result = self._to_pixmap(edge)
        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)
        return result

##
# @class PrewittEdge
# @brief Performs Prewitt edge detection.
# @inherits AbstractEdgeDetector
#
# @details
# Prewitt operator estimates gradient direction similar to Sobel.
#
# @see AbstractEdgeDetector
class PrewittEdge(AbstractEdgeDetector):
    def detect(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()
        edge = prewitt(self._load_gray_image())
        edge = self._apply_threshold(edge)
        result = self._to_pixmap(edge)
        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)
        return result


# =====================================================================
#                      HANDLER CLASS
# =====================================================================

##
# @class EdgeDetectionHandler
# @brief Unified interface for running and undoing edge detection operations.
#
# @details
# Provides a GUI-safe encapsulation of any edge detector.
# Enables command-pattern-based execution and undo.
#
# @see AbstractEdgeDetector
class EdgeDetectionHandler:
    def __init__(self, operation: AbstractEdgeDetector):
        """
        @brief Initializes the handler with a detector object.
        @param operation Concrete subclass of AbstractEdgeDetector.
        """
        self._operation = operation

    def set_operation(self, operation: AbstractEdgeDetector):
        """
        @brief Swaps out the active detector object.
        @param operation A new edge detector.
        """
        self._operation = operation

    def run(self):
        """
        @brief Executes the detection operation.
        @return QPixmap: Resulting edge map.
        """
        return self._operation.detect()

    def undo(self):
        """
        @brief Reverts the last edge detection result from GUI.
        """
        self._operation.undo()



"""
edge = SobelEdge("resim.jpg", threshold)
result = edge.detect()

seg = ChanVeseSegmentation("resim.jpg")
result = seg.apply()

gray = RGBToGray("resim.jpg")
result = gray.apply()


handler = EdgeDetectionHandler(SobelEdge("resim.jpg", 100))
result = handler.run()


handler = SegmentationHandler(ChanVeseSegmentation("resim.jpg"))
result = handler.run()

"""