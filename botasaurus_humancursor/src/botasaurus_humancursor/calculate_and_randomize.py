import random
import math
import pytweening


def calculate_absolute_offset(element, relative_position, rect=None):
    """Calculates the absolute offset based on relative position"""
    if rect is None:
        # Get element position using _get_bounding_rect_with_iframe_offset
        rect = element._get_bounding_rect_with_iframe_offset()
    
    element_width = rect["width"]
    element_height = rect["height"]
    
    x_exact_off = element_width * relative_position[0]
    y_exact_off = element_height * relative_position[1]
    
    return [int(x_exact_off), int(y_exact_off)] 


def generate_random_curve_parameters(driver, pre_origin, post_destination):
    """Generates random parameters for the curve, the tween, number of knots, distortion, target points and boundaries"""
    
    # Get window size using Botasaurus's run_js
    window_size = driver.run_js("""
        return {
            width: document.documentElement.clientWidth || window.innerWidth || document.body.clientWidth,
            height: document.documentElement.clientHeight || window.innerHeight || document.body.clientHeight
        };
    """)

    web = True
    viewport_width, viewport_height = window_size['width'],window_size['height']
    
    min_width, max_width = viewport_width * 0.15, viewport_width * 0.85
    min_height, max_height = viewport_height * 0.15, viewport_height * 0.85

    # tween_options = [
    #     pytweening.easeOutExpo,
    #     # pytweening.easeInOutQuint,
    #     # pytweening.easeInOutSine,
    #     # pytweening.easeInOutQuart,
    #     # pytweening.easeInOutExpo,
    #     # pytweening.easeInOutCubic,
    #     # pytweening.easeInOutCirc,
    #     # pytweening.linear,
    #     pytweening.easeOutSine,
    #     pytweening.easeOutQuart,
    #     pytweening.easeOutQuint,
    #     pytweening.easeOutCubic,
    #     pytweening.easeOutCirc,
    # ]
    # lesser detected option's
    tween_options = [
        pytweening.easeInOutQuad,
        pytweening.easeOutQuad,
        pytweening.easeInOutSine,
        pytweening.easeInOutCubic,
        pytweening.easeInOutQuint
    ]
    tween = random.choice(tween_options)
    # tween = pytweening.easeOutQuad
    # print(tween.__name__)
    offset_boundary_x = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    offset_boundary_y = random.choice(
        random.choices(
            [range(20, 45), range(45, 75), range(75, 100)], [0.2, 0.65, 15]
        )[0]
    )
    knots_count = random.choices(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [0.15, 0.36, 0.17, 0.12, 0.08, 0.04, 0.03, 0.02, 0.015, 0.005],
    )[0]

    distortion_mean = random.choice(range(80, 110)) / 100
    distortion_st_dev = random.choice(range(85, 110)) / 100
    distortion_frequency = random.choice(range(25, 70)) / 100

    target_points = generate_target_points(pre_origin, post_destination)
    

    if (
            min_width > pre_origin[0]
            or max_width < pre_origin[0]
            or min_height > pre_origin[1]
            or max_height < pre_origin[1]
    ):
        offset_boundary_x = 1
        offset_boundary_y = 1
        knots_count = 1
    if (
            min_width > post_destination[0]
            or max_width < post_destination[0]
            or min_height > post_destination[1]
            or max_height < post_destination[1]
    ):
        offset_boundary_x = 1
        offset_boundary_y = 1
        knots_count = 1
    return (
        offset_boundary_x,
        offset_boundary_y,
        knots_count,
        distortion_mean,
        distortion_st_dev,
        distortion_frequency,
        tween,
        target_points,
    )
def calculate_step_count(
    distance: float,
) -> int:
    """
    Calculate the ideal number of steps for a drag operation based on distance.
    
    Args:
        distance: The pixel distance between origin and destination
    
    Returns:
        The calculated step count, clamped between min_steps and max_steps
    """
    # Define step parameters based on distance ranges
    if distance <= 500:
        min_steps, max_steps, base_distance = 40, 50, 500
    elif distance <= 1000:
        min_steps, max_steps, base_distance = 50, 60, 1000
    elif distance <= 1500:
        min_steps, max_steps, base_distance = 60, 70, 1500
    elif distance <= 2000:
        min_steps, max_steps, base_distance = 70, 80, 2000
    else:
        #  generate_distance((0,0), (1920, 1080)) = 2202
        min_steps, max_steps, base_distance = 80, 100, 2202
        
    # Calculate step count that scales with distance
    step_count = min_steps + (distance / base_distance) * (max_steps - min_steps)
    
    # Round down and apply some randomness for variability
    step_count = int(step_count * random.uniform(0.9, 1.1))
    
    return max(min_steps, min(max_steps, step_count))


def generate_distance(pre_origin, post_destination):
    x1, y1 = pre_origin
    x2, y2 = post_destination
    dist = math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
    return dist

def generate_target_points(pre_origin, post_destination):
    dist = generate_distance(pre_origin, post_destination)
    return calculate_step_count(dist)
