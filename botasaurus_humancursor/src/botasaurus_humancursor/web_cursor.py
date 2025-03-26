from time import sleep
import random
from typing import Union
from botasaurus_driver import Driver, cdp, BrowserTab
from botasaurus_driver.driver import Element
from .web_adjuster import WebAdjuster

class WebCursor:
    def __init__(self, driver: Driver, _dot_name: str):
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

    def move_to(
            self,
            element: Union[Element, list],
            relative_position: list = None,
            absolute_offset: bool = False,
            origin_coordinates=None,
            steady=False
    ):
        """Moves to element or coordinates with human curve"""
        if not self.scroll_into_view_of_element(element):
            return False
        if origin_coordinates is None:
            origin_coordinates = self.origin_coordinates
        self.origin_coordinates = self.human.move_to(
            element,
            origin_coordinates=origin_coordinates,
            absolute_offset=absolute_offset,
            relative_position=relative_position,
            steady=steady
        )
        return self.origin_coordinates

    def click(
            self,
            element: Union[Element, list],
            number_of_clicks: int = 1,
            click_duration: float = 0,
            relative_position: list = None,
            absolute_offset: bool = False,
            origin_coordinates=None,
            steady=False
    ):
        """Moves to element or coordinates with human curve, and clicks on it a specified number of times, default is 1"""
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

    def _click(self, number_of_clicks: int = 1, click_duration: float = 0):
        """Performs the click action"""
        for _ in range(number_of_clicks):
                # Using CDP to perform mousedown
                self.driver.run_cdp_command(
                    cdp.input_.dispatch_mouse_event(
                        "mousePressed",
                        x=self.origin_coordinates[0],
                        y=self.origin_coordinates[1],
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
                    )
                )
                if click_duration:
                    sleep(click_duration)
                else:
                    self.random_natural_sleep()
                # Using CDP to perform mouseup and click
                self.driver.run_cdp_command(
                    cdp.input_.dispatch_mouse_event(
                        "mouseReleased",
                        x=self.origin_coordinates[0],
                        y=self.origin_coordinates[1],
                        button=cdp.input_.MouseButton("left"),
                        click_count=1,
                        )
                )
                self.random_natural_sleep()
        return True

    def move_by_offset(self, x: int, y: int, steady=False):
        """Moves the cursor with human curve, by specified number of x and y pixels"""
        self.origin_coordinates = self.human.move_to([x, y],  absolute_offset=True, steady=steady)
        return True

    def drag_and_drop(
            self,
            drag_from_element: Union[Element, list],
            drag_to_element: Union[Element, list],
            drag_from_relative_position: list = None,
            drag_to_relative_position: list = None,
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
            self.driver.run_cdp_command(
                cdp.input_.dispatch_mouse_event(
                    "mousePressed",
                    x=self.origin_coordinates[0],
                    y=self.origin_coordinates[1],
                    button=cdp.input_.MouseButton("left"),
                    click_count=1
                )
            )
            if drag_to_relative_position is None:
                self.move_to(drag_to_element, steady=steady)
            else:
                self.move_to(
                    drag_to_element, relative_position=drag_to_relative_position, steady=steady
                )
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

    def control_scroll_bar(
            self,
            scroll_bar_element: Union[Element, list],
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
            element = self.driver.get_element_at_point(x=element[0],y=element[1])
            # an iframe, no need to scroll into view
            if isinstance(element, BrowserTab):
              return True

            self.scroll_to_element(element)
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

    def show_cursor(self):
        self.driver.run_js('''if (!window.dEl) {
    let dot
    function displayRedDot() {
        // Get the cursor position
        const x = event.clientX
        const y = event.clientY

        if (!dot) {
            // Create a new span element for the red dot if it doesn't exist
            dot = document.createElement("span")
            // Style the dot with CSS
            dot.style.position = "fixed"
            dot.style.width = "5px"
            dot.style.height = "5px"
            dot.style.borderRadius = "50%"
            dot.style.backgroundColor = "#E7010A"
            // Add the dot to the page
            document.body.prepend(dot)
        }

        // Update the dot's position
        dot.style.left = x + "px"
        dot.style.top = y + "px"
    }

    // Add event listener to update the dot's position on mousemove
    document.addEventListener("mousemove", displayRedDot)
    window.dEl = dot
}''')

    def hide_cursor(self):
        self.driver.run_js('''window.dEl?.remove()''')