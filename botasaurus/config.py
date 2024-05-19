# BROWSER CONFIGS

block_images_config = {
    "block_images": True,
}

block_images_and_css_config = {
    "block_images_and_css": True,
}

headless_config = {
    "headless": True,
}

reuse_driver_config = {
    "reuse_driver": True,
}

## MAJOR CONFIGS
production_config = {
    "raise_exception": True,
    "create_error_logs": False,
    "close_on_crash": True,
    "output": None,
}

production_error_tolerant_config = {
    **production_config,
    "raise_exception": False,
}

## Browser Configs
production_browser_config = {
    **production_config,
    **headless_config,
    **block_images_and_css_config,
    **reuse_driver_config,
}


production_browser_error_tolerant_config = {
    **production_browser_config,
    "raise_exception": False,
}
