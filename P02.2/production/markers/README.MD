Markers - program to simplify putting markers, visible bounds and a grid on your screen if your camera software does not allow that by default
Code was tested on Python 3.2.3 with PyQt 4.10 (Qt 4.8.4) library
code by Konstantin Glazyrin (lorcat at do no evil google)

License:
The source code license is GPL v.3 license in agreement with PyQt restrictions.
Please see http://www.gnu.org/licenses/gpl-3.0.txt in order to acquaint yourself with the terms of GPL v.3

Operational system:
Cross platform, but please make sure that your Window Manager can produce transparency effects

Uses:
- To find a center and size of the custom shape visualized on your computer screen by the camera.
- Mark specific points on video stream produced by your camera and shown on your computer screen.
- Measure some distances.

PROS:
Program saves last position (+size, style, additional cursor position) of the marker window and, thus, makes it easier to recover
previous settings when needed

ToDo:
Need to do simple documentation, describe all key-bindings and current implementations

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

Current key bindings:
# Marker window
    # Movement
Left/Right/Up/Down - move marker window (when activated) with large step
ALT+Left/Right/Up/Down - move marker window (when activated) with small step

    # Resizing
SHIFT+Left/Right/Up/Down - move marker window (when activated) with large step
SHIFT+ALT+Left/Right/Up/Down - move marker window (when activated) with small step

    # switch different shapes
F2-F7
or
TAB - switch through different shapes; Tab switching allows change of marker line width
      currently implemented shapes:
       SQUARE, CIRCLE, RECTANGLE, ELLIPSE, SHORT BOUNDS, GRID

    # marker color change
CTRL+Tab - cycle through implemented colors

    # marker style adjustment
c - switch central cursor ON or OFF
f - switch marker frame (not central cursor) ON or OFF
+ - increase marker opacity
- - decrease marker opacity
    
    # show hide marker window
no key bindings - please do that through main Marker Control Window

# additional cursor
    # movement
CTRL+Left/Right/Up/Down - move additional cursorwindow (when visible) with small step
CTRL+ALT+Left/Right/Up/Down - move additional cursorwindow (when visible) with large step

    # style adjustment for the additional cursor
CTRL-c - switch ON or OFF visibility of the additional cursor

-------------------------------
-------------------------------
All key bindings are duplicated throught the Marker Control window actions