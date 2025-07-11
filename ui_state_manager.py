##
# @file ui_state_manager.py
# @brief UI state logic abstraction for PyQt5-based image processing applications.
#
# @details
# This module defines a set of classes that control the enabled/disabled state of GUI elements
# in a structured and modular way based on different stages of image processing (initial, image loaded, processed).
#
# ### Object-Oriented Design:
# - **Abstraction**: Common interface via @ref AbstractUIStateManager.
# - **Inheritance**: @ref StandardUIStateManager derives from the abstract base.
# - **Polymorphism**: Dynamic dispatch of UI update logic based on current application state.
# - **Encapsulation**: Keeps logic for UI element control isolated from business logic.
#
# @note Designed to improve maintainability and testability of GUI update routines.
#
# @author Doğukan AVCI
# @date May 7, 2025
#

from abc import ABC, abstractmethod

##
# @class AbstractUIStateManager
# @brief Abstract interface for controlling the enabled/disabled state of UI widgets.
# @inherits ABC
#
# @details
# This base class provides the structure for all UI state managers. It defines the contract
# for when and how GUI elements should be enabled or disabled during various processing stages.
#
# ### Use Case:
# - Disable UI during processing
# - Enable UI after image load
# - Enable export options after result is ready
#
# @note All subclasses must implement the three abstract methods.
# @see StandardUIStateManager
class AbstractUIStateManager(ABC):
    def __init__(self, ui):
        """
        @brief Constructs the manager with the UI reference.
        @param ui (object): Main window object containing PyQt5 widgets.
        """
        self.ui = ui

    ##
    # @brief Disables all interactive UI components.
    #
    # @note Intended to be used when processing is ongoing or the system is in an idle state.
    @abstractmethod
    def disable_all(self):
        pass

    ##
    # @brief Enables GUI buttons and actions after an image is loaded.
    #
    # @note Designed to allow access to processing tools and image export functions.
    @abstractmethod
    def enable_after_image_loaded(self):
        pass

    ##
    # @brief Enables UI components required after a processing operation is completed.
    #
    # @note Primarily affects output-related controls.
    @abstractmethod
    def enable_after_processing(self):
        pass


##
# @class StandardUIStateManager
# @brief Default implementation of @ref AbstractUIStateManager for typical GUI workflows.
# @inherits AbstractUIStateManager
#
# @details
# This class manipulates the UI state based on the stage of user interaction:
# - After image is loaded → enable processing options
# - After processing → enable export and undo/redo
# - On reset → disable everything
#
# @see AbstractUIStateManager
class StandardUIStateManager(AbstractUIStateManager):

    def disable_all(self):
        """
        @brief Disables all UI widgets, actions, and menu items.
        """
        ui = self.ui
        # Toolbar and menu actions
        ui.actionSave_Output.setEnabled(False)
        ui.actionSave_As_Output.setEnabled(False)
        ui.actionSource.setEnabled(False)
        ui.actionOutput.setEnabled(False)
        ui.actionUndo_Output.setEnabled(False)
        ui.actionRedo_Output.setEnabled(False)
        ui.clearSource_Button_menu.setEnabled(False)
        ui.clearOutput_Button_menu.setEnabled(False)

        # Image conversion and processing
        ui.actionRGB_to_Grayscale.setEnabled(False)
        ui.actionRGB_to_HSV.setEnabled(False)
        ui.actionMulti_Otsu_Thresholding.setEnabled(False)
        ui.actionChan_Vese_Segmentation.setEnabled(False)
        ui.actionMorphological_Snakes.setEnabled(False)
        ui.actionRoberts.setEnabled(False)
        ui.actionSobel.setEnabled(False)
        ui.actionScharr.setEnabled(False)
        ui.actionPrewitt.setEnabled(False)

        # Button controls
        ui.GrayScale_button.setEnabled(False)
        ui.HSV_button.setEnabled(False)
        ui.multiotsu_Button.setEnabled(False)
        ui.chanvese_Buttton.setEnabled(False)
        ui.morp_button.setEnabled(False)
        ui.Roberts_button.setEnabled(False)
        ui.Sobel_button.setEnabled(False)
        ui.Scharr_button.setEnabled(False)
        ui.Prewitt_button.setEnabled(False)
        ui.Source_Clear_button.setEnabled(False)
        ui.Source_Export_button.setEnabled(False)
        ui.Clear_Output_button.setEnabled(False)
        ui.Save_Output_button.setEnabled(False)
        ui.Save_as_Output_button.setEnabled(False)
        ui.Export_Output_button.setEnabled(False)
        ui.Redo_Output_button.setEnabled(False)
        ui.Undo_Output_button.setEnabled(False)

    def enable_after_image_loaded(self):
        """
        @brief Enables processing and export buttons once an image is loaded.
        """
        ui = self.ui
        # Buttons
        ui.GrayScale_button.setEnabled(True)
        ui.HSV_button.setEnabled(True)
        ui.multiotsu_Button.setEnabled(True)
        ui.chanvese_Buttton.setEnabled(True)
        ui.morp_button.setEnabled(True)
        ui.Roberts_button.setEnabled(True)
        ui.Sobel_button.setEnabled(True)
        ui.Scharr_button.setEnabled(True)
        ui.Prewitt_button.setEnabled(True)
        ui.Source_Clear_button.setEnabled(True)
        ui.Source_Export_button.setEnabled(True)

        # Menu Actions
        ui.actionRGB_to_Grayscale.setEnabled(True)
        ui.actionRGB_to_HSV.setEnabled(True)
        ui.actionMulti_Otsu_Thresholding.setEnabled(True)
        ui.actionChan_Vese_Segmentation.setEnabled(True)
        ui.actionMorphological_Snakes.setEnabled(True)
        ui.actionRoberts.setEnabled(True)
        ui.actionSobel.setEnabled(True)
        ui.actionScharr.setEnabled(True)
        ui.actionPrewitt.setEnabled(True)
        ui.actionSource.setEnabled(True)
        ui.clearSource_Button_menu.setEnabled(True)

    def enable_after_processing(self):
        """
        @brief Enables output-related options (save, export, undo) after processing is done.
        """
        ui = self.ui
        ui.Save_Output_button.setEnabled(True)
        ui.Save_as_Output_button.setEnabled(True)
        ui.Export_Output_button.setEnabled(True)
        ui.Clear_Output_button.setEnabled(True)
        ui.Redo_Output_button.setEnabled(True)
        ui.Undo_Output_button.setEnabled(True)
        ui.actionSave_Output.setEnabled(True)
        ui.actionSave_As_Output.setEnabled(True)
        ui.actionOutput.setEnabled(True)
        ui.actionUndo_Output.setEnabled(True)
        ui.actionRedo_Output.setEnabled(True)
        ui.clearOutput_Button_menu.setEnabled(True)
