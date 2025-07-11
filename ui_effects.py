##
# @file ui_effects.py
# @brief Utility functions for applying animation effects in PyQt5 interfaces.
#
# @details
# This module enhances PyQt5 GUI interactivity by providing reusable animation utilities.
# It supports fade-in transitions and button "pop" effects with elastic feedback.
#
# Though classless, it demonstrates key OOP concepts:
# - **Abstraction**: Animation logic is encapsulated in clearly defined reusable functions.
# - **Encapsulation**: Internal animation states are retained by setting references on widgets.
# - **Memory Safety**: Prevents premature deletion of animations via instance binding (`_fade_anim`, `_hover_anim`).
#
# These utilities are used in the AgriEdge GUI to improve responsiveness and user feedback.
#
# @author Doğukan AVCI
# @date May 7, 2025
#

from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup

##
# @brief Applies a smooth fade-in animation to a widget.
#
# @details
# Uses `QGraphicsOpacityEffect` and `QPropertyAnimation` to gradually increase the opacity of the widget
# from 0 to 1 over the specified duration. Internally binds the animation to the widget instance
# to avoid garbage collection issues.
#
# ### Parameters:
# @param widget QWidget to animate
# @param duration Duration in milliseconds (default = 1000 ms)
#
# ### Example Usage:
# @code
# fade_in_widget(self.label_output)
# @endcode
#
# @note Stores reference as `widget._fade_anim` to keep animation alive.
def fade_in_widget(widget, duration=1000):
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.start()

    # Prevent garbage collection
    widget._fade_anim = animation

##
# @brief Applies an animated "pop" effect on a QPushButton.
#
# @details
# This function makes the button grow slightly and then return to original size,
# producing a visual response to hover or click events. It creates two
# geometry animations chained in a `QSequentialAnimationGroup`.
#
# ### Parameters:
# @param button QPushButton to animate
# @param scale Scale multiplier (default = 1.05)
# @param duration Duration for each animation phase in milliseconds (default = 150)
#
# ### Example Usage:
# @code
# animate_button_hover(self.Start_Button)
# @endcode
#
# @note Animation reference is saved as `button._hover_anim` to prevent early deletion.
def animate_button_hover(button, scale=1.05, duration=150):
    geom = button.geometry()
    w, h = geom.width(), geom.height()
    dw, dh = int(w * (scale - 1)), int(h * (scale - 1))
    enlarged = geom.adjusted(-dw // 2, -dh // 2, dw // 2, dh // 2)

    # Grow animation
    grow = QPropertyAnimation(button, b"geometry")
    grow.setDuration(duration)
    grow.setStartValue(geom)
    grow.setEndValue(enlarged)
    grow.setEasingCurve(QEasingCurve.OutQuad)

    # Shrink animation
    shrink = QPropertyAnimation(button, b"geometry")
    shrink.setDuration(duration)
    shrink.setStartValue(enlarged)
    shrink.setEndValue(geom)
    shrink.setEasingCurve(QEasingCurve.InQuad)

    # Chain grow and shrink animations
    group = QSequentialAnimationGroup()
    group.addAnimation(grow)
    group.addAnimation(shrink)
    group.start()

    # Prevent garbage collection
    button._hover_anim = group
