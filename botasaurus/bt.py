from .calc_max_parallel_browsers import (
    calc_max_parallel_browsers,
    BrowserResourceConfig,
)
from .output import (
    read_json,
    write_json,
    read_temp_json,
    write_temp_json,
    read_csv,
    write_csv,
    read_temp_csv,
    write_temp_csv,
    read_html,
    write_html,
    read_temp_html,
    write_temp_html,
    read_file,
    write_file,
    save_image,
    read_excel,
    write_excel,
    read_temp_excel,
    write_temp_excel,
    zip_files,
)
from .formats import Formats
from .beep_utils import prompt
from .utils import remove_nones, uniquify_strings 
from .list_utils import flatten , flatten_deep
from .cl import snakecase, camelcase, remove_commas, snakecase_keys, camelcase_keys, select, extract_numbers, extract_number, extract_links, extract_emails, extract_otps, is_email_verification_link, extract_email_verification_links, extract_ld_json, extract_meta_content, extract_path_from_link, extract_domain_from_link, wrap_in_dict, extract_from_dict, join_link, join_dicts, join_with_commas, join_with_newlines, trim_and_collapse_spaces, link_matches_path, filter_links_by_path, pluralize, find_value_in_dict, sort_object_by_keys, rename_keys, base64_decode
from .env import IS_PRODUCTION, IS_DOCKER , get_os
from .string_utils import hide_text_with_asterisk, ht