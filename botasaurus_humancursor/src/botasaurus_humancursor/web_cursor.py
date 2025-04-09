from time import sleep
import random
from typing import Union, Callable, Optional
from botasaurus_driver import Driver, cdp, BrowserTab
from botasaurus_driver.driver import Element
from .web_adjuster import WebAdjuster

class WebCursor:
    def __init__(self, driver: Driver, _dot_name: str = "dot"):
        """
        Initialize WebCursor with a Botasaurus driver
        
        Args:
            driver: Botasaurus Driver instance
            _dot_name: Name of the dot element for cursor visualization
        """
        self.driver = driver
        self.human = WebAdjuster(self.driver)
        self.origin_coordinates = [0, 0]
        self._dot_name = _dot_name
        self._show_cursor_movements = True

    def move_mouse_to_point(self, x: int, y: int, is_jump=False,steady=False):
        """Moves the cursor with human curve, by specified number of x and y pixels"""
        # self.show_cursor()
        self.origin_coordinates = self.human.move_to([x, y], self,is_jump, steady=steady)
        return True
    
    def move_to(
            self,
            element: Union[Element, tuple[int, int] ],
            is_jump=False,
            relative_position: tuple[int, int]  = None,
            absolute_offset: bool = True,
            origin_coordinates=None,
            steady=False,
            is_mouse_pressed=False
    ):
        """Moves to element or coordinates with human curve"""
        if not self.scroll_into_view_of_element(element):
            return False
        if origin_coordinates is None:
            origin_coordinates = self.origin_coordinates
        # self.show_cursor()
        self.origin_coordinates = self.human.move_to(
            element,
            self,
            is_jump,
            origin_coordinates=origin_coordinates,
            absolute_offset=absolute_offset,
            relative_position=relative_position,
            steady=steady,
            is_mouse_pressed=is_mouse_pressed,
        )
        return self.origin_coordinates

    def click(
            self,
            element: Union[Element, tuple[int, int] ],
            number_of_clicks: int = 1,
            click_duration: float = 0,
            skip_move: bool = False,
            relative_position: tuple[int, int]  = None,
            absolute_offset: bool = True,
            origin_coordinates=None,
            steady=False
    ):
        """Moves to element or coordinates with human curve, and clicks on it a specified number of times, default is 1
        
        Args:
            skip_move: If True, skips the mouse movement and clicks at the current position (or target coordinates directly)
        """
        if not skip_move:
            self.move_to(
                element,
                origin_coordinates=origin_coordinates,
                absolute_offset=absolute_offset,
                relative_position=relative_position,
                steady=steady
            )
            self.random_natural_sleep()
        
        self._click(number_of_clicks=number_of_clicks, click_duration=click_duration)
        return True

    def random_natural_sleep(self):
        sleep(random.randint(170, 280) / 1000)

    def _click(self, number_of_clicks: int = 1, release_condition: Optional[Callable[[], bool]] = None, release_condition_check_interval: float = 0.5, click_duration: Optional[float] = None,) -> None:
        """Performs the click action"""
        for _ in range(number_of_clicks):
            # Using CDP to perform mousedown
            self.mouse_press(
                x=self.origin_coordinates[0],
                y=self.origin_coordinates[1],
            )
            if click_duration:
                sleep(click_duration)
            else:
                self.random_natural_sleep()

            if release_condition is not None:
                try:
                  while not release_condition():
                    sleep(release_condition_check_interval)
                except Exception as e:
                    raise e
                finally:
                    self.mouse_release(
                        x=self.origin_coordinates[0],
                        y=self.origin_coordinates[1],
                    )
                    self.random_natural_sleep()
            else:
                self.mouse_release(
                    x=self.origin_coordinates[0],
                    y=self.origin_coordinates[1],
                )
                self.random_natural_sleep()

    def mouse_press(self,x,y):
        self.driver.run_cdp_command(
                    cdp.input_.dispatch_mouse_event(
                        "mousePressed",
                        x=x,
                        y=y,
                        modifiers=0, 
                        buttons=1, 
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
                    )
                )

    def mouse_release(self,x,y):
        self.driver.run_cdp_command(
                    cdp.input_.dispatch_mouse_event(
                        "mouseReleased",
                        x=x,
                        y=y,
                        modifiers=0, 
                        # no buttons
                        buttons=0, 
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
                    )
                )



    def mouse_press_and_hold(self, x: int, y: int, release_condition: Optional[Callable[[], bool]] = None, release_condition_check_interval: float = 0.5, click_duration: Optional[float] = None):
        """Moves the cursor with human curve, by specified number of x and y pixels"""
        self.move_mouse_to_point(x,y)
        self._click(release_condition=release_condition, release_condition_check_interval=release_condition_check_interval, click_duration=click_duration)
        return True
    
    

    def drag_and_drop(
            self,
            drag_from_element: Union[Element, tuple[int, int] ],
            drag_to_element: Union[Element, tuple[int, int] ],
            drag_from_relative_position: tuple[int, int]  = None,
            drag_to_relative_position: tuple[int, int]  = None,
            steady=False
    ):
        """Moves to element or coordinates, clicks and holds, dragging it to another element, with human curve"""
        if drag_from_relative_position is None:
            self.move_to(drag_from_element, steady=steady)
        else:
            self.move_to(
                drag_from_element, relative_position=drag_from_relative_position, steady=steady
            )

        if drag_to_element is None:
            self._click()
        else:
        # Click and hold using CDP
            self.mouse_press(
                x=self.origin_coordinates[0],
                y=self.origin_coordinates[1],
            )
            if drag_to_relative_position is None:
                self.move_to(drag_to_element, steady=steady, is_mouse_pressed=True)
            else:
                self.move_to(
                    drag_to_element, relative_position=drag_to_relative_position, steady=steady, is_mouse_pressed=True
                )
            self.mouse_release(
                        x=self.origin_coordinates[0],
                        y=self.origin_coordinates[1],
                    )
        return True

    def control_scroll_bar(
            self,
            scroll_bar_element: Union[Element, tuple[int, int] ],
            amount_by_percentage: list,
            orientation: str = "horizontal",
            steady=False
    ):
        """Adjusts any scroll bar on the webpage, by the amount you want in float number from 0 to 1
        representing percentage of fullness, orientation of the scroll bar must also be defined by user
        horizontal or vertical"""
        direction = True if orientation == "horizontal" else False

        self.move_to(scroll_bar_element)
        # Click and hold using CDP
        self.driver.run_cdp_command(
            cdp.input_.dispatch_mouse_event(
                "mousePressed",
                x=self.origin_coordinates[0],
                y=self.origin_coordinates[1],
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
            )
        )
        
        # Move to target position
        if direction:
            self.move_to(
                scroll_bar_element,
                relative_position=[amount_by_percentage, random.randint(0, 100) / 100],
                steady=steady
            )
        else:
            self.move_to(
                scroll_bar_element,
                relative_position=[random.randint(0, 100) / 100, amount_by_percentage],
                steady=steady
            )

        # Release using CDP
        self.driver.run_cdp_command(
            cdp.input_.dispatch_mouse_event(
                "mouseReleased",
                x=self.origin_coordinates[0],
                y=self.origin_coordinates[1],
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
            )
        )

        return True

    def scroll_into_view_of_element(self, element: Element):
        """Scrolls the element into viewport, if not already in it"""
        if isinstance(element, Element):
            self.scroll_to_element(element)
            return True
        elif isinstance(element, (list, tuple)):
            try:
                element = self.driver.get_element_at_point(x=element[0],y=element[1])
                # an iframe, no need to scroll into view
                if isinstance(element, BrowserTab):
                    return True

                self.scroll_to_element(element)
                return True
            except:
              return True
            
            
        else:
            print("Incorrect Element or Coordinates values!")
            return False

    def scroll_to_element(self, element):
        scrolling_code = """(element)=>{
              var rect = element.getBoundingClientRect();
              return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
              );            
}"""
        is_in_viewport = element.run_js(scrolling_code)
        if not is_in_viewport:
            element.scroll_into_view()
            sleep(random.uniform(0.8, 1.4))
    
#     def _generate_show_cursor_code(self):
#         return f'''if (!window.{self._dot_name}) {{
#     function displayRedDot(x,y) {{
#         // Get the cursor position
#         // Get or create the dot
#         let dot = window.{self._dot_name};
#         if (!dot) {{
#             // Create a new span element for the red dot
#             dot = document.createElement("span");
#             // Style the dot with CSS
#             dot.style.position = "fixed";
#             dot.style.width = "5px";
#             dot.style.height = "5px";
#             dot.style.borderRadius = "50%";
#             dot.style.backgroundColor = "#E7010A";
#             dot.style.pointerEvents = "none"; // Make it non-interactive
#             dot.style.zIndex = "999999"; // Ensure it's on top
#             // Add the dot to the page
#             document.body.prepend(dot);
#             window.{self._dot_name} = dot;
#         }}
#         // Update the dot's position
#         dot.style.left = x + "px";
#         dot.style.top = y + "px";
#     }}
#     // Add event listener to update the dot's position on mousemove
#     // document.addEventListener("mousemove", (e) => displayRedDot(event.clientX, event.clientY));
# }}'''

    def _generate_update_cursor_position_code(self, x: int, y: int):
        return f'''function displayRedDot(x,y) {{
        // Get the cursor position
        // Get or create the dot
        let dot = HTMLMarqueeElement.prototype.{self._dot_name};
        if (!dot) {{
            // Create a new span element for the red dot
            dot = document.createElement("span");
            // Style the dot with CSS
            dot.style.position = "fixed";
            dot.style.width = "5px";
            dot.style.height = "5px";
            dot.style.borderRadius = "50%";
            dot.style.backgroundColor = "#E7010A";
            dot.style.pointerEvents = "none"; // Make it non-interactive
            dot.style.zIndex = "999999"; // Ensure it's on top
            // Add the dot to the page
            document.body.prepend(dot);
            HTMLMarqueeElement.prototype.{self._dot_name} = dot;
        }}
        // Update the dot's position
        dot.style.left = x + "px";
        dot.style.top = y + "px";
    }}
    displayRedDot({x}, {y})'''

    def update_cursor_position(self, x: int, y: int):
        self.driver.run_js(self._generate_update_cursor_position_code(x,y))

    # def show_cursor(self):
    #     self.driver.run_js(self._generate_show_cursor_code())

    def _generate_delete_cursor_code(self):
        return f'''HTMLMarqueeElement.prototype.{self._dot_name}?.remove()'''

    def delete_cursor(self):
                self.driver.run_js(self._generate_delete_cursor_code())

    def hide_cursor_movements(self):
        self._show_cursor_movements = False
