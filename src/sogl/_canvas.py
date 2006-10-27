# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:         canvas.py
# Purpose:      The canvas class
#
# Author:       Klaus Zimmermann <klaus.zimmermann@fmf.uni-freiburg.de>
# Heavily based on work by Pierre Hjälm. See OGL in wxPython.
#
# Created:      26-10-2006
# SVN-ID:       $Id: $
# Copyright:    (c) 2006 Klaus Zimmermann - 2004 Pierre Hjälm - 1998 Julian Smart
# Licence:      wxWindows license
#----------------------------------------------------------------------------

import wx
from _lines import LineShape
from _composit import *

NoDragging, StartDraggingLeft, ContinueDraggingLeft, StartDraggingRight, ContinueDraggingRight = 0, 1, 2, 3, 4

KEY_SHIFT, KEY_CTRL = 1, 2



# Helper function: True if 'contains' wholly contains 'contained'.
def WhollyContains(contains, contained):
    xp1, yp1 = contains.GetX(), contains.GetY()
    xp2, yp2 = contained.GetX(), contained.GetY()
    
    w1, h1 = contains.GetBoundingBoxMax()
    w2, h2 = contained.GetBoundingBoxMax()
    
    left1 = xp1 - w1 / 2.0
    top1 = yp1 - h1 / 2.0
    right1 = xp1 + w1 / 2.0
    bottom1 = yp1 + h1 / 2.0
    
    left2 = xp2 - w2 / 2.0
    top2 = yp2 - h2 / 2.0
    right2 = xp2 + w2 / 2.0
    bottom2 = yp2 + h2 / 2.0
    
    return ((left1 <= left2) and (top1 <= top2) and (right1 >= right2) and (bottom1 >= bottom2))
    


class ShapeCanvas(wx.ScrolledWindow):
    def __init__(self, parent = None, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.BORDER, name = "ShapeCanvas"):
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)

        self._dragState = NoDragging
        self._draggedShape = None
        self._oldDragX = 0
        self._oldDragY = 0
        self._firstDragX = 0
        self._firstDragY = 0
        self._checkTolerance = True
        self._quickEditMode = False
        self._snapToGrid = True
        self._gridSpacing = 5.0
        self._shapeList = []
        self._mouseTolerance = DEFAULT_MOUSE_TOLERANCE

        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_MOUSE_EVENTS(self, self.OnMouseEvent)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        
        dc.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.Clear()

        self.Redraw(dc)

    def OnMouseEvent(self, evt):
        dc = wx.ClientDC(self)
        self.PrepareDC(dc)
        
        x, y = evt.GetLogicalPosition(dc)

        keys = 0
        if evt.ShiftDown():
            keys |= KEY_SHIFT
        if evt.ControlDown():
            keys |= KEY_CTRL

        dragging = evt.Dragging()

        # Check if we're within the tolerance for mouse movements.
        # If we're very close to the position we started dragging
        # from, this may not be an intentional drag at all.
        if dragging:
            if self._checkTolerance:
                # the difference between two logical coordinates is a logical coordinate
                dx = abs(x - self._firstDragX) 
                dy = abs(y - self._firstDragY)
                toler = self.GetMouseTolerance()
                if (dx <= toler) and (dy <= toler):
                    return
            # If we've ignored the tolerance once, then ALWAYS ignore
            # tolerance in this drag, even if we come back within
            # the tolerance range.
            self._checkTolerance = False

        # Dragging - note that the effect of dragging is left entirely up
        # to the object, so no movement is done unless explicitly done by
        # object.
        if dragging and self._draggedShape and self._dragState == StartDraggingLeft:
            self._dragState = ContinueDraggingLeft

            # If the object isn't m_draggable, transfer message to canvas
            dragCandidate=self._draggedShape
            while dragCandidate and (not dragCandidate.IsSensitiveTo(OP_DRAG_LEFT)):
                dragCandidate=dragCandidate._parent
            if dragCandidate:
                dragCandidate.GetEventHandler().OnBeginDragLeft(x, y, keys, self._draggedAttachment)
            else:
                self._draggedShape = None
                self.OnBeginDragLeft(x, y, keys)

            self._oldDragX, self._oldDragY = x, y

        elif dragging and self._draggedShape and self._dragState == ContinueDraggingLeft:
            # Continue dragging
            self._draggedShape.GetEventHandler().OnDragLeft(False, self._oldDragX, self._oldDragY, keys, self._draggedAttachment)
            self._draggedShape.GetEventHandler().OnDragLeft(True, x, y, keys, self._draggedAttachment)
            self._oldDragX, self._oldDragY = x, y

        elif evt.LeftUp() and self._draggedShape and self._dragState == ContinueDraggingLeft:
            self._dragState = NoDragging
            self._checkTolerance = True

            self._draggedShape.GetEventHandler().OnDragLeft(False, self._oldDragX, self._oldDragY, keys, self._draggedAttachment)
            self._draggedShape.GetEventHandler().OnEndDragLeft(x, y, keys, self._draggedAttachment)
            self._draggedShape = None

        elif dragging and self._draggedShape and self._dragState == StartDraggingRight:
            self._dragState = ContinueDraggingRight
            if self._draggedShape.IsSensitiveTo( OP_DRAG_RIGHT ):
                self._draggedShape.GetEventHandler().OnBeginDragRight(x, y, keys, self._draggedAttachment)
            else:
                self._draggedShape = None
                self.OnBeginDragRight(x, y, keys)
            self._oldDragX, self._oldDragY = x, y

        elif dragging and self._draggedShape and self._dragState == ContinueDraggingRight:
            # Continue dragging
            self._draggedShape.GetEventHandler().OnDragRight(False, self._oldDragX, self._oldDragY, keys, self._draggedAttachment)
            self._draggedShape.GetEventHandler().OnDragRight(True, x, y, keys, self._draggedAttachment)
            self._oldDragX, self._oldDragY = x, y

        elif evt.RightUp() and self._draggedShape and self._dragState == ContinueDraggingRight:
            self._dragState = NoDragging
            self._checkTolerance = True

            self._draggedShape.GetEventHandler().OnDragRight(False, self._oldDragX, self._oldDragY, keys, self._draggedAttachment)
            self._draggedShape.GetEventHandler().OnEndDragRight(x, y, keys, self._draggedAttachment)
            self._draggedShape = None

        # All following events sent to canvas, not object
        elif dragging and not self._draggedShape and self._dragState == StartDraggingLeft:
            self._dragState = ContinueDraggingLeft
            self.OnBeginDragLeft(x, y, keys)
            self._oldDragX, self._oldDragY = x, y

        elif dragging and not self._draggedShape and self._dragState == ContinueDraggingLeft:
            # Continue dragging
            self.OnDragLeft(False, self._oldDragX, self._oldDragY, keys)
            self.OnDragLeft(True, x, y, keys)
            self._oldDragX, self._oldDragY = x, y                

        elif evt.LeftUp() and not self._draggedShape and self._dragState == ContinueDraggingLeft:
            self._dragState = NoDragging
            self._checkTolerance = True

            self.OnDragLeft(False, self._oldDragX, self._oldDragY, keys)
            self.OnEndDragLeft(x, y, keys)
            self._draggedShape = None

        elif dragging and not self._draggedShape and self._dragState == StartDraggingRight:
            self._dragState = ContinueDraggingRight
            self.OnBeginDragRight(x, y, keys)
            self._oldDragX, self._oldDragY = x, y

        elif dragging and not self._draggedShape and self._dragState == ContinueDraggingRight:
            # Continue dragging
            self.OnDragRight(False, self._oldDragX, self._oldDragY, keys)
            self.OnDragRight(True, x, y, keys)
            self._oldDragX, self._oldDragY = x, y

        elif evt.RightUp() and not self._draggedShape and self._dragState == ContinueDraggingRight:
            self._dragState = NoDragging
            self._checkTolerance = True

            self.OnDragRight(False, self._oldDragX, self._oldDragY, keys)
            self.OnEndDragRight(x, y, keys)
            self._draggedShape = None

        # Non-dragging events
        elif evt.IsButton():
            self._checkTolerance = True

            # Find the nearest object
            attachment = 0

            nearest_object, attachment = self.FindShape(x, y)
            if nearest_object: # Object event
                if evt.LeftDown():
                    self._draggedShape = nearest_object
                    self._draggedAttachment = attachment
                    self._dragState = StartDraggingLeft
                    self._firstDragX = x
                    self._firstDragY = y

                elif evt.LeftUp():
                    # N.B. Only register a click if the same object was
                    # identified for down *and* up.
                    if nearest_object == self._draggedShape:
                        clickCandidate=nearest_object
                        while clickCandidate and (not clickCandidate.IsSensitiveTo(OP_CLICK_LEFT)):
                            clickCandidate=clickCandidate._parent
                        if clickCandidate:
                            clickCandidate.GetEventHandler().OnLeftClick(x, y, keys, attachment)
                    self._draggedShape = None
                    self._dragState = NoDragging

                elif evt.LeftDClick():
                    nearest_object.GetEventHandler().OnLeftDoubleClick(x, y, keys, attachment)
                    self._draggedShape = None
                    self._dragState = NoDragging

                elif evt.RightDown():
                    self._draggedShape = nearest_object
                    self._draggedAttachment = attachment
                    self._dragState = StartDraggingRight
                    self._firstDragX = x
                    self._firstDragY = y

                elif evt.RightUp():
                    if nearest_object == self._draggedShape:
                        nearest_object.GetEventHandler().OnRightClick(x, y, keys, attachment)
                    self._draggedShape = None
                    self._dragState = NoDragging

            else: # Canvas event
                if evt.LeftDown():
                    self._draggedShape = None
                    self._dragState = StartDraggingLeft
                    self._firstDragX = x
                    self._firstDragY = y

                elif evt.LeftUp():
                    self.OnLeftClick(x, y, keys)
                    self._draggedShape = None
                    self._dragState = NoDragging

                elif evt.RightDown():
                    self._draggedShape = None
                    self._dragState = StartDraggingRight
                    self._firstDragX = x
                    self._firstDragY = y

                elif evt.RightUp():
                    self.OnRightClick(x, y, keys)
                    self._draggedShape = None
                    self._dragState = NoDragging

    def FindShape(self, x, y, info = None, notObject = None):
        nearest = 100000.0
        nearest_attachment = 0
        nearest_object = None

        # Go backward through the object list, since we want:
        # (a) to have the control points drawn LAST to overlay
        #     the other objects
        # (b) to find the control points FIRST if they exist

        rl = self.GetShapeList()[:]
        rl.reverse()
        for object in rl:
            # First pass for lines, which might be inside a container, so we
            # want lines to take priority over containers. This first loop
            # could fail if we clickout side a line, so then we'll
            # try other shapes.
            if object.IsShown() and \
               isinstance(object, LineShape) and \
               object.HitTest(x, y) and \
               ((info == None) or isinstance(object, info)) and \
               (not notObject or not notObject.HasDescendant(object)):
                temp_attachment, dist = object.HitTest(x, y)
                # A line is trickier to spot than a normal object.
                # For a line, since it's the diagonal of the box
                # we use for the hit test, we may have several
                # lines in the box and therefore we need to be able
                # to specify the nearest point to the centre of the line
                # as our hit criterion, to give the user some room for
                # manouevre.
                if dist < nearest:
                    nearest = dist
                    nearest_object = object
                    nearest_attachment = temp_attachment

        for object in rl:
            # On second pass, only ever consider non-composites or
            # divisions. If children want to pass up control to
            # the composite, that's up to them.
            if (object.IsShown() and 
                   (isinstance(object, DivisionShape) or 
                    not isinstance(object, CompositeShape)) and 
                    object.HitTest(x, y) and 
                    (info == None or isinstance(object, info)) and 
                    (not notObject or not notObject.HasDescendant(object))):
                temp_attachment, dist = object.HitTest(x, y)
                if not isinstance(object, LineShape):
                    # If we've hit a container, and we have already
                    # found a line in the first pass, then ignore
                    # the container in case the line is in the container.
                    # Check for division in case line straddles divisions
                    # (i.e. is not wholly contained).
                    if not nearest_object or not (isinstance(object, DivisionShape) or WhollyContains(object, nearest_object)):
                        nearest_object = object
                        nearest_attachment = temp_attachment
                        break

        return nearest_object, nearest_attachment

    def OnLeftClick(self, x, y, keys = 0):
        pass

    def OnRightClick(self, x, y, keys = 0):
        pass

    def OnDragLeft(self, draw, x, y, keys = 0):
        pass

    def OnBeginDragLeft(self, x, y, keys = 0):
        pass

    def OnEndDragLeft(self, x, y, keys = 0):
        pass

    def OnDragRight(self, draw, x, y, keys = 0):
        pass

    def OnBeginDragRight(self, x, y, keys = 0):
        pass

    def OnEndDragRight(self, x, y, keys = 0):
        pass

    def Redraw(self, dc):
        """Draw the shapes in the diagram on the specified device context."""
        if self._shapeList:
            self.SetCursor(wx.HOURGLASS_CURSOR)
            for object in self._shapeList:
                object.Draw(dc)
            self.SetCursor(wx.STANDARD_CURSOR)

    def Clear(self, dc):
        """Clear the specified device context."""
        dc.Clear()

    def AddShape(self, object, addAfter = None):
        """Adds a shape to the diagram. If addAfter is not None, the shape
        will be added after addAfter.
        """
        if not object in self._shapeList:
            if addAfter:
                self._shapeList.insert(self._shapeList.index(addAfter) + 1, object)
            else:
                self._shapeList.append(object)

            object.SetCanvas(self)

    def InsertShape(self, object):
        """Insert a shape at the front of the shape list."""
        self._shapeList.insert(0, object)

    def RemoveShape(self, object):
        """Remove the shape from the diagram (non-recursively) but do not
        delete it.
        """
        if object in self._shapeList:
            self._shapeList.remove(object)
            
    def RemoveAllShapes(self):
        """Remove all shapes from the diagram but do not delete the shapes."""
        self._shapeList = []

    def DeleteAllShapes(self):
        """Remove and delete all shapes in the diagram."""
        for shape in self._shapeList[:]:
            if not shape.GetParent():
                self.RemoveShape(shape)
                shape.Delete()
                
    def ShowAll(self, show):
        """Call Show for each shape in the diagram."""
        for shape in self._shapeList:
            shape.Show(show)

    def DrawOutline(self, dc, x1, y1, x2, y2):
        """Draw an outline rectangle on the current device context."""
        dc.SetPen(wx.Pen(wx.Color(0, 0, 0), 1, wx.DOT))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        dc.DrawLines([[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]])

    def RecentreAll(self, dc):
        """Make sure all text that should be centred, is centred."""
        for shape in self._shapeList:
            shape.Recentre(dc)

    def FindShape(self, id):
        """Return the shape for the given identifier."""
        for shape in self._shapeList:
            if shape.GetId() == id:
                return shape
        return None

    def Snap(self, x, y):
        """'Snaps' the coordinate to the nearest grid position, if
        snap-to-grid is on."""
        if self._snapToGrid:
            return self._gridSpacing * int(x / self._gridSpacing + 0.5), self._gridSpacing * int(y / self._gridSpacing + 0.5)
        return x, y

    def SetGridSpacing(self, spacing): 
        """Sets grid spacing.""" 
        self._gridSpacing = spacing 
 
    def SetSnapToGrid(self, snap): 
        """Sets snap-to-grid mode.""" 
        self._snapToGrid = snap 

    def GetGridSpacing(self):
        """Return the grid spacing."""
        return self._gridSpacing

    def GetSnapToGrid(self):
        """Return snap-to-grid mode."""
        return self._snapToGrid

    def SetQuickEditMode(self, mode):
        """Set quick-edit-mode on of off.

        In this mode, refreshes are minimized, but the diagram may need
        manual refreshing occasionally.
        """
        self._quickEditMode = mode

    def GetQuickEditMode(self):
        """Return quick edit mode."""
        return self._quickEditMode

    def SetMouseTolerance(self, tolerance):
        """Set the tolerance within which a mouse move is ignored.

        The default is 3 pixels.
        """
        self._mouseTolerance = tolerance

    def GetMouseTolerance(self):
        """Return the tolerance within which a mouse move is ignored."""
        return self._mouseTolerance

    def GetShapeList(self):
        """Return the internal shape list."""
        return self._shapeList

    def GetCount(self):
        """Return the number of shapes in the diagram."""
        return len(self._shapeList)
