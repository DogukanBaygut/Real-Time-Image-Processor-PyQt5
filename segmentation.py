##
# @file segmentation.py
# @brief Implements modular and polymorphic image segmentation algorithms.
#
# @details
# This module is part of the AgriEdge image processing pipeline.
# It includes multiple segmentation techniques that follow a common abstract interface.
# The system is built on strong Object-Oriented Programming (OOP) design:
#
# - **Abstraction** via `SegmentationOperation` base class
# - **Inheritance** by `MultiOtsuSegmentation`, `ChanVeseSegmentation`, and `MorphologicalSnakesSegmentation`
# - **Polymorphism** through the overridden `apply()` method
# - **Encapsulation** and **Data Hiding** via protected members and clean interfaces
#
# These operations are GUI-integrated via QLabel output updates and include undo support.
#
# @date May 6, 2025
# @author Doğukan AVCI
#

from abc import ABC, abstractmethod
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
from skimage.filters import threshold_multiotsu
from skimage.segmentation import chan_vese, morphological_chan_vese
from PyQt5.QtGui import QImage, QPixmap

# =====================================================================
#                      ABSTRACT SEGMENTATION BASE
# =====================================================================

##
# @class SegmentationOperation
# @brief Abstract base class for all segmentation operations.
# @inherits ABC
#
# @details
# Provides a unified interface for segmentation classes. Implements utility
# methods for undo, image conversion, and result display. Forces subclasses
# to override the `apply()` method for polymorphic execution.
#
# ### OOP Highlights:
# - Abstraction: Requires concrete subclasses to implement `apply()`
# - Encapsulation: QLabel and image path are protected
# - Data Hiding: `__image_path` is private and accessed via getter/setter
#
# @note This class should not be instantiated directly.
# @see MultiOtsuSegmentation, ChanVeseSegmentation, MorphologicalSnakesSegmentation
class SegmentationOperation(ABC):
    def __init__(self, image_path, label_output=None):
        """
        @brief Constructor
        @param image_path (str): Path to the input image file
        @param label_output (QLabel): Output display widget for result
        """
        self.__image_path = image_path
        self._label_output = label_output
        self._prev_pixmap = None

    def get_image_path(self):
        """
        @brief Gets the current image path.
        @return str: The image path.
        """
        return self.__image_path

    def set_image_path(self, new_path):
        """
        @brief Sets a new image path.
        @param new_path (str): New image path
        """
        self.__image_path = new_path

    def undo(self):
        """
        @brief Restores the previous segmentation result (if available).
        @note Requires `_label_output` and `_prev_pixmap` to be valid.
        """
        if self._label_output and self._prev_pixmap:
            self._label_output.setPixmap(self._prev_pixmap)
            self._label_output.setScaledContents(True)

    @abstractmethod
    def apply(self):
        """
        @brief Abstract method for executing the segmentation.
        @return QPixmap: The segmented image.
        """
        pass

    def _to_qimage(self, gray: np.ndarray) -> QImage:
        """
        @brief Converts a grayscale NumPy image to QImage.
        @param gray (np.ndarray): 2D image data
        @return QImage
        """
        h, w = gray.shape
        return QImage(gray.data, w, h, w, QImage.Format_Grayscale8)

    def _to_qpixmap(self, gray: np.ndarray) -> QPixmap:
        """
        @brief Converts a grayscale NumPy image to QPixmap.
        @param gray (np.ndarray): 2D image
        @return QPixmap
        """
        return QPixmap.fromImage(self._to_qimage(gray))


# =====================================================================
#                     CONCRETE SEGMENTATION CLASSES
# =====================================================================

##
# @class MultiOtsuSegmentation
# @brief Segments the image using Multi-Otsu thresholding.
# @inherits SegmentationOperation
#
# @details
# Applies multi-class thresholding using skimage’s `threshold_multiotsu()`.
# Useful for distinguishing multiple intensity regions.
#
# ### Characteristics:
# - Inherits and overrides `apply()`
# - Provides multi-region segmentation
#
# @example
# handler = SegmentationHandler(MultiOtsuSegmentation(path))
# handler.run()
class MultiOtsuSegmentation(SegmentationOperation):
    def apply(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()

        img = imread(self.get_image_path())
        if img.ndim == 3 and img.shape[2] == 4:
            img = img[:, :, :3]
        gray = rgb2gray(img) if img.ndim == 3 else img

        thresholds = threshold_multiotsu(gray, classes=3)
        regions = np.digitize(gray, bins=thresholds)
        output_img = (regions * (255 / regions.max())).astype(np.uint8)
        result = self._to_qpixmap(output_img)

        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)

        return result


##
# @class ChanVeseSegmentation
# @brief Active contour segmentation using Chan-Vese model.
# @inherits SegmentationOperation
#
# @details
# A region-based segmentation method that uses level-set evolution.
# Best suited for images with smooth boundaries.
#
# ### Characteristics:
# - Non-edge-based segmentation
# - Tolerant to noise and intensity variation
#
# @see morphological_chan_vese
class ChanVeseSegmentation(SegmentationOperation):
    def apply(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()

        img = imread(self.get_image_path())
        if img.ndim == 3 and img.shape[2] == 4:
            img = img[:, :, :3]
        gray = rgb2gray(img) if img.ndim == 3 else img

        cv_result = chan_vese(
            gray,
            mu=0.25,
            lambda1=1,
            lambda2=1,
            tol=1e-3,
            max_num_iter=200,
            dt=0.5,
            init_level_set="checkerboard"
        )

        output_img = (cv_result * 255).astype(np.uint8)
        result = self._to_qpixmap(output_img)

        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)

        return result


##
# @class MorphologicalSnakesSegmentation
# @brief Active contour segmentation using Morphological Snakes.
# @inherits SegmentationOperation
#
# @details
# Implements morphological snakes algorithm for efficient shape evolution.
# Smoother and faster than classical Chan-Vese on many cases.
#
# @note This method is particularly robust to noise and initialization.
class MorphologicalSnakesSegmentation(SegmentationOperation):
    def apply(self):
        if self._label_output:
            self._prev_pixmap = self._label_output.pixmap()

        img = imread(self.get_image_path())
        if img.ndim == 3 and img.shape[2] == 4:
            img = img[:, :, :3]
        gray = rgb2gray(img) if img.ndim == 3 else img

        morph_result = morphological_chan_vese(
            gray,
            num_iter=200,
            init_level_set="checkerboard",
            smoothing=3
        )

        output_img = (morph_result * 255).astype(np.uint8)
        result = self._to_qpixmap(output_img)

        if self._label_output:
            self._label_output.setPixmap(result)
            self._label_output.setScaledContents(True)

        return result

# =====================================================================
#                       HANDLER CLASS FOR SEGMENTATION
# =====================================================================

##
# @class SegmentationHandler
# @brief Encapsulates and executes any segmentation operation.
#
# @details
# Accepts any subclass of @ref SegmentationOperation and executes it
# polymorphically. Used by threaded processing systems or GUI triggers.
#
# ### Design Notes:
# - Applies inversion of control
# - Follows the Command design pattern for UI interactions
#
# @see SegmentationOperation
class SegmentationHandler:
    def __init__(self, operation: SegmentationOperation):
        """
        @brief Constructor
        @param operation (SegmentationOperation): A concrete segmentation object.
        """
        self._operation = operation

    def run(self):
        """
        @brief Executes the assigned segmentation operation.
        @return QPixmap: The resulting image.
        """
        return self._operation.apply()

    def undo(self):
        """
        @brief Triggers the undo logic for the segmentation.
        """
        self._operation.undo()
