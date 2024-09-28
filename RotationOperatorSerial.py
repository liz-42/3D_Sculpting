import bpy
import serial
import math
from bpy.props import IntProperty, FloatProperty
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector


class ModalOperator(bpy.types.Operator):
    """Rotate an object with serial input"""
    bl_idname = "object.rotation_operator_serial" # to call script with shortcuts
    bl_label = "Rotation Modal Operator Serial"
    
    # cursor positions on object
    x_loc = 0
    y_loc = 0
    z_loc = 0
    
    # values for object rotation
    first_val_x: FloatProperty()
    first_val_y: FloatProperty()
    first_val_z: FloatProperty()
    
    radius = 0 # keep track of the size of the sphere where new material is added
    max_radius = 0 # for range sensor position
    

    def modal(self, context, event):
        if event.type == 'TIMER':
            # read ultrasonic range data
            if self.range.in_waiting != 0:
                dist_data = float(self.range.readline().strip())
                self.max_radius = (dist_data - 10)/5 # in cms - 5 is the neutral 0 point on the distance slider
            # read accelerometer data
            if self.accel.in_waiting != 0:
                tilt_data = int(self.accel.readline().strip().decode('ascii'))
            
                if tilt_data > 200:
                    # rotate object forward
                    context.object.rotation_euler = (self.first_val_x + 0.1, self.first_val_y, self.first_val_z)
                    self.first_val_x = context.object.rotation_euler.x
                    rotation = get_rotation(context.object)
                    # add material to object if max radius is greater than threshold
                    if abs(self.max_radius) > 0.05:
                        # use draw tool if positive max radius
                        if self.max_radius > 0.05:
                            bpy.ops.paint.brush_select(sculpt_tool="DRAW", toggle=False)
                            bpy.data.brushes["SculptDraw"].strength = 0.6
                            x = self.x_loc
                            y = self.radius * math.sin(math.radians(rotation[0]))
                            z = self.radius * math.cos(math.radians(rotation[0]))
                            self.radius += (0.6/500)
                        else:
                            # use carving tool if negative max radius
                            bpy.ops.paint.brush_select(sculpt_tool="DRAW_SHARP", toggle=False)
                            bpy.data.brushes["SculptDraw"].strength = 0.1
                            x = self.x_loc
                            y = self.radius * math.sin(math.radians(rotation[0]))
                            z = self.radius * math.cos(math.radians(rotation[0]))
                            self.radius -= (0.1/1000)
                        coordinates = [(x,y,z)]
                        #print(min(self.radius, self.max_radius), self.radius, self.max_radius)
                        
                        strokes = []
                        for i, coordinate in enumerate(coordinates):
                            stroke = {
                            "name": "stroke",
                            "mouse": (0,0),
                            "mouse_event": (0,0),
                            "x_tilt": 0.0,
                            "y_tilt": 0.0,
                            "pen_flip" : False,
                            "is_start": True if i==0 else False,
                            "location": coordinate,
                            "size": 10,
                            "pressure": abs(self.max_radius),
                            "time": float(i)
                        }
                        strokes.append(stroke)
                        bpy.ops.sculpt.brush_stroke(context_override(), stroke=strokes)
                        
                elif tilt_data < -200:
                    # rotate object backward
                    context.object.rotation_euler = (self.first_val_x - 0.1, self.first_val_y, self.first_val_z)
                    self.first_val_x = context.object.rotation_euler.x
                    rotation = get_rotation(context.object)  
                    # use draw tool if positive max radius
                    if self.max_radius > 0.05:
                        bpy.ops.paint.brush_select(sculpt_tool="DRAW", toggle=False)
                        bpy.data.brushes["SculptDraw"].strength = 0.6
                        x = self.x_loc
                        y = self.radius * math.sin(math.radians(rotation[0]))
                        z = self.radius * math.cos(math.radians(rotation[0]))
                        self.radius += (0.6/500)
                    else:
                        # use carve tool if negative max radius
                        bpy.ops.paint.brush_select(sculpt_tool="DRAW_SHARP", toggle=False)
                        bpy.data.brushes["SculptDraw"].strength = 0.1
                        x = self.x_loc
                        y = self.radius * math.sin(math.radians(rotation[0]))
                        z = self.radius * math.cos(math.radians(rotation[0]))
                        self.radius -= (0.1/1000)
                    coordinates = [(x,y,z)]
                    print(min(self.radius, self.max_radius), self.radius, self.max_radius)
                        
                    strokes = []
                    for i, coordinate in enumerate(coordinates):
                        stroke = {
                            "name": "stroke",
                            "mouse": (0,0),
                            "mouse_event": (0,0),
                            "x_tilt": 0.0,
                            "y_tilt": 0.0,
                            "pen_flip" : False,
                            "is_start": True if i==0 else False,
                            "location": coordinate,
                            "size": 10,
                            "pressure": abs(self.max_radius),
                            "time": float(i)
                        }
                    strokes.append(stroke)
                    bpy.ops.sculpt.brush_stroke(context_override(), stroke=strokes)       
        
        if event.type == "LEFTMOUSE":
            if event.value == "PRESS":
                # get current x,y,z position of cursor and update radius
                cursor_location = region_2d_to_location_3d(context.region,context.space_data.region_3d,(event.mouse_region_x, event.mouse_region_y),Vector((0, 0, 0)))
                context.scene.cursor.location = cursor_location
                print(context.scene.cursor.location)
                self.x_loc = cursor_location.x
                self.y_loc = cursor_location.y
                self.z_loc = cursor_location.z
                self.radius = cursor_location.z
        
        if event.type == 'ESC':
            # reset to default position
            context.object.rotation_euler = (0.0, 0.0, 0.0)
            context.window_manager.event_timer_remove(self._timer)
            
            self.accel.close()
            self.range.close()
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        ''' Initialization function '''
        if context.object:
            context.object.rotation_mode = "XYZ"
            
            self.first_val_x = context.object.rotation_euler.x
            self.first_val_y = context.object.rotation_euler.y
            self.first_val_z = context.object.rotation_euler.z
            
            self.accel = serial.Serial("COM6", 115200)
            self.range = serial.Serial("COM5", 115200)
            
            self._timer = context.window_manager.event_timer_add(0.01, window=context.window)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
        
def context_override():
    ''' Helper function to support sculpting in modal operator '''
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene} 
                    
def get_rotation(object):
    ''' Helper function to get rotation angle of the object '''
    matrix_rotation = object.matrix_world
    euler_rotation = matrix_rotation.to_euler()
    deg_rotation = [math.degrees(a) for a in euler_rotation]
    return deg_rotation
       

def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)
    

if __name__ == "__main__":
    register()

    # call modal
    bpy.ops.object.rotation_operator_serial('INVOKE_DEFAULT')