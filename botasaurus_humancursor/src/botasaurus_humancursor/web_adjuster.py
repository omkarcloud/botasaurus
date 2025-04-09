import random
from time import sleep

from botasaurus_driver import Driver, cdp
from .human_curve_generator import HumanizeMouseTrajectory
from .calculate_and_randomize import generate_random_curve_parameters, calculate_absolute_offset


class WebAdjuster:
    def __init__(self, driver: Driver):
        """
        Initialize WebAdjuster with a Botasaurus driver
        
        Args:
            driver: Botasaurus Driver instance
        """
        self.driver = driver
        self.origin_coordinate = [0, 0]

    def do_move(self, x,y,
                web_cursor,
                is_mouse_pressed=False):
        if is_mouse_pressed:
            self.driver.run_cdp_command(cdp.input_.dispatch_mouse_event(
                                "mouseMoved",
                                x=x,
                                y=y,
                                button=cdp.input_.MouseButton("left"), 
                        ))
            if web_cursor._show_cursor_movements:
                web_cursor.update_cursor_position(x,y)
                sleep(0.003)
            # needed to show cordinates movments
        else: 
            self.driver.run_cdp_command(cdp.input_.dispatch_mouse_event(
                                "mouseMoved",
                                x=x,
                                y=y,
                        ))
            if web_cursor._show_cursor_movements:
                web_cursor.update_cursor_position(x,y)
            # sleep(0.003 )


    def fix_mouse_move_cursor(self, web_cursor):
        name = web_cursor._dot_name + 't'
        # fix the mouse event's dispatched by cdp
        # as MouseEvent.prototype.screenY is equal to clientY but should be clientY + window.screenY
        self.driver.run_js(f"""if (!HTMLMarqueeElement.prototype.{name}) {{
    Object.defineProperty(MouseEvent.prototype, 'screenX', {{
        get: function () {{
            return this.clientX + window.screenX;
        }}
    }});
    Object.defineProperty(MouseEvent.prototype, 'screenY', {{
        get: function () {{
            return this.clientY + window.screenY;
        }}
    }});
    HTMLMarqueeElement.prototype.{name} = true;
}}                           
        """)
    def move_to(
        self,
        element_or_pos,
        web_cursor, 
        is_jump=False,
        origin_coordinates=None,
        absolute_offset=True,
        relative_position=None,
        human_curve=None,
        steady=False,
        is_mouse_pressed=False,
          # Added new argument (alternative names: direct_move, immediate, skip_animation, fast_move, instant_move)
    ):
        """Moves the cursor, trying to mimic human behaviour!
        
        Args:
            is_jump: If True, moves directly to the target coordinates without human-like movement
        """
        origin = origin_coordinates
        if origin_coordinates is None:
            origin = self.origin_coordinate

        pre_origin = tuple(origin)
        if isinstance(element_or_pos, (list,tuple)):
            if absolute_offset:
                x, y = element_or_pos[0], element_or_pos[1]
            else:
                x, y = (
                    element_or_pos[0] + pre_origin[0],
                    element_or_pos[1] + pre_origin[1],
                )
        else:
            # Get element position using Botasaurus's _get_bounding_rect_with_iframe_offset, with fallback if needed
            try:
                rect = element_or_pos._get_bounding_rect_with_iframe_offset()
            except Exception as e:
                print("Error obtaining bounding rect for element:", e)
                if hasattr(element_or_pos, "_elem"):
                    raw = element_or_pos._elem
                    rect = self.driver.run_js("(function(el){var r=el.getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height};})(arguments[0]);", [raw])
                else:
                    print("Element does not support _elem attribute, cannot get position.")
                    return origin
            if rect.get("width", 0) == 0 or rect.get("height", 0) == 0:
                print("Could not find position for", element_or_pos)
                return origin
            destination = {"x": rect.get("x", 0), "y": rect.get("y", 0)}
            
            if relative_position is None:
                x_random_off = random.choice(range(20, 80)) / 100
                y_random_off = random.choice(range(20, 80)) / 100

                # Get element size from bounding rect
                element_width = rect["width"]
                element_height = rect["height"]
                
                x, y = destination["x"] + (
                    element_width * x_random_off
                ), destination["y"] + (element_height * y_random_off)
            else:
                abs_exact_offset = calculate_absolute_offset(
                    element_or_pos, relative_position, rect
                )
                x_exact_off, y_exact_off = abs_exact_offset[0], abs_exact_offset[1]
                x, y = destination["x"] + x_exact_off, destination["y"] + y_exact_off

        if is_jump:  # If is_jump is True, move directly to the target coordinates
            self.fix_mouse_move_cursor(web_cursor)
            self.do_move(
                x=x,
                y=y,
                web_cursor=web_cursor,
                is_mouse_pressed=is_mouse_pressed
            )
            self.origin_coordinate = [x, y]
            return [x, y]

        # Original human-like movement code
        (
            offset_boundary_x,
            offset_boundary_y,
            knots_count,
            distortion_mean,
            distortion_st_dev,
            distortion_frequency,
            tween,
            target_points,
        ) = generate_random_curve_parameters(
            self.driver, [origin[0], origin[1]], [x, y]
        )
        if steady:
            offset_boundary_x, offset_boundary_y = 10, 10
            distortion_mean, distortion_st_dev, distortion_frequency = 1.2, 1.2, 1
        if not human_curve:
            human_curve = HumanizeMouseTrajectory(
                [origin[0], origin[1]],
                [x, y],
                offset_boundary_x=offset_boundary_x,
                offset_boundary_y=offset_boundary_y,
                knots_count=knots_count,
                distortion_mean=distortion_mean,
                distortion_st_dev=distortion_st_dev,
                distortion_frequency=distortion_frequency,
                tween=tween,
                target_points=target_points,
            )
        self.fix_mouse_move_cursor(web_cursor)
        for point in human_curve.points:
            # Move to each point in the curve
            self.do_move(
                    x=point[0],
                    y=point[1],
                    web_cursor=web_cursor,
                    is_mouse_pressed=is_mouse_pressed
            )
            
            # Update the origin coordinates
            origin[0], origin[1] = point[0], point[1]
        self.origin_coordinate = [x, y]
        return [x, y]