import json
from casefy import snakecase, titlecase
import json

from .errors import JsonHTTPResponseWithMessage

class BaseFilter:
    def __init__(self, field, label=None):
        self.field = field
        self.label = label

        class_name = snakecase(self.__class__.__name__)
        self.id = f"{field}_{class_name}"

    def should_filter(self, filter_value):
        # General logic to determine if this filter should be applied
        return filter_value is not None

    def map_filter_value(self, filter_value):
        # Default implementation just returns the filter value as is.
        # Override this in subclasses as needed.
        return filter_value

    def filter(self, filter_value, data_value):
        # To be implemented by subclasses
        raise NotImplementedError

    def to_json(self):
        # Generate a dictionary that represents the JSON structure
        filter_json = {
            "id": self.id,
            "type": self.__class__.__name__,
            "label": self.label or self.get_label(),
        }
        return filter_json

    def get_label(self):
        raise NotImplementedError


class _NumericFilterBase(BaseFilter):
    def should_filter(self, filter_value):
        # Filter should be applied if filter_value is a number (int or float) and not None
        return filter_value is not None and isinstance(filter_value, (int, float))


class MinNumberInput(_NumericFilterBase):
    def filter(self, filter_value, data_value):
        # If data_value is None, it automatically fails the minimum number condition
        if isinstance(data_value, (int, float)):
            return data_value >= filter_value
        else:
            # Handle non-numeric data_value as per your requirements (e.g., log a warning or raise an error)
            return False

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Min {title_cased_field}"


class MaxNumberInput(_NumericFilterBase):
    def filter(self, filter_value, data_value):
        # If data_value is None, it automatically fails the maximum number condition
        if isinstance(data_value, (int, float)):
            return data_value <= filter_value
        else:
            # Handle non-numeric data_value as per your requirements
            return False

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Max {title_cased_field}"


class _Checkbox(BaseFilter):
    def should_filter(self, filter_value):
        return filter_value is True


class IsTrueCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        return data_value is True

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Has {title_cased_field}"


class IsFalseCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        return data_value is False

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Does Not Have {title_cased_field}"


class IsNullCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        return data_value is None

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Does Not Have {title_cased_field}"


class IsNotNullCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        return data_value is not None

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Has {title_cased_field}"


class IsTruthyCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        return data_value

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Has {title_cased_field}"


class IsFalsyCheckbox(_Checkbox):
    def filter(self, filter_value, data_value):
        # Filter passes if data_value is falsy (evaluates to False in a boolean context)
        return not data_value

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Does Not Have {title_cased_field}"


class _DropdownFilterBase(BaseFilter):
    def __init__(self, field, options, label=None, case_insensitive=True):
        super().__init__(field, label)

        self.options = options if options else []
        self.case_insensitive = case_insensitive

        if self.options:
            self.validate_options(self.options)

    def validate_options(self, options):
        if not all("value" in option and "label" in option for option in options):
            raise ValueError("Each option must have 'value' and 'label' keys.")
        if not all(
            isinstance(option["value"], str) and isinstance(option["label"], str)
            for option in options
        ):
            raise TypeError("'value' and 'label' must be of type str.")
        if len(set(option["value"] for option in options)) != len(options):
            raise ValueError("'value' must be unique for each option.")

    def to_json(self):
        # Call the BaseFilter's to_json method and extend its functionality
        filter_json = super().to_json()

        # Add the options attribute specific to the _DropdownFilterBase class
        filter_json["options"] = self.options

        return filter_json


class SingleSelectDropdown(_DropdownFilterBase):
    def filter(self, filter_value, data_value):
        if isinstance(data_value, str):
            comparison_value = (
                data_value.lower() if self.case_insensitive else data_value
            )
            return comparison_value == filter_value
        elif isinstance(data_value, list):
            for item in data_value:
                if isinstance(item, str):  # Ensure the item is a string
                    # Apply case insensitivity if needed and compare directly
                    if (
                        item.lower() if self.case_insensitive else item
                    ) == filter_value:
                        return True
        return False

    def map_filter_value(self, filter_value):
        if self.case_insensitive and isinstance(filter_value, str):
            return filter_value.lower()
        return filter_value

    def should_filter(self, filter_value):
        # General logic to determine if this filter should be applied
        return isinstance(filter_value, str) and filter_value.strip()

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} Is"


class BoolSelectDropdown(_DropdownFilterBase):

    def __init__(self, field,  label=None, prioritize_no=False):
        super().__init__(field, label)

        if prioritize_no:
            self.options =[{"value":"no","label":"No"},{"value":"yes","label":"Yes"},]
        else:
            self.options =[{"value":"yes","label":"Yes"},{"value":"no","label":"No"}]

        # todo remove
        self.validate_options(self.options)

    def filter(self, filter_value, data_value):
        if filter_value == "yes":
            if data_value:
                return True
            else:
                return False
        elif filter_value == "no":
            if not data_value:
                return True
            else:
                return False

        return False

    def should_filter(self, filter_value):
        return isinstance(filter_value, str) and filter_value.strip()

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Has {title_cased_field}"


class MultiSelectDropdown(_DropdownFilterBase):
    def filter(self, filter_value, data_value):
        if isinstance(data_value, str):
            comparison_value = (
                data_value.lower() if self.case_insensitive else data_value
            )
            return comparison_value in filter_value
        elif isinstance(data_value, list):
            # Directly iterate over data_value and check against filter_value
            for item in data_value:
                if isinstance(item, str):
                    # Apply case insensitivity if needed
                    item = item.lower() if self.case_insensitive else item
                    if item in filter_value:
                        return True
        return False

    def map_filter_value(self, filter_value):
        if not isinstance(filter_value, (set, list, tuple)):
            raise JsonHTTPResponseWithMessage(
                "filter_value must be a set, list, or tuple for MultiSelectDropdown"
            )

        if filter_value and not all(isinstance(val, str) for val in filter_value):
            raise JsonHTTPResponseWithMessage("filter_value must only contain strings")

        if self.case_insensitive:
            return set(val.lower() for val in filter_value if isinstance(val, str))
        else:
            return set(filter_value)

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} Is One Of"


class SearchTextInput(BaseFilter):
    def filter(self, filter_value, data_value):
        # Filter passes if the filter_value (search term) is a substring of data_value
        # Assumes data_value is a string or can be cast to a string
        if isinstance(data_value, str):
            return filter_value in data_value.lower()
        return False

    def should_filter(self, filter_value):
        # General logic to determine if this filter should be applied
        return isinstance(filter_value, str) and filter_value.strip()

    def map_filter_value(self, filter_value):
        # Default implementation just returns the filter value as is.
        # Override this in subclasses as needed.
        return filter_value.strip().lower()

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Search {title_cased_field}"


def apply_filters(data_records, filters_data, available_filters):
    if not filters_data:
        return data_records

    # Determine which filters are applicable
    applicable_filters = [
        filter_obj
        for filter_obj in available_filters
        if filter_obj.should_filter(filters_data.get(filter_obj.id))
    ]

    # Update filters_data by mapping each filter's value using its map_filter_value method
    for filter_obj in applicable_filters:
        original_filter_value = filters_data[filter_obj.id]
        # Use the map_filter_value method to transform the filter value
        transformed_filter_value = filter_obj.map_filter_value(original_filter_value)
        # Update the filter value in filters_data with the transformed value
        filters_data[filter_obj.id] = transformed_filter_value

    # Apply each filter to the data records
    filtered_records = []
    for record in data_records:
        passes_all_filters = True
        for filter_obj in applicable_filters:
            if filter_obj.field not in record:
                rep = json.dumps(record, indent=4)
                if len(rep) >= 1003:
                    rep = rep[:1000] + "..."
                raise JsonHTTPResponseWithMessage(
                    f"Filter field {filter_obj.field} not found in data record: {rep}."
                )
            if not filter_obj.filter(
                filters_data[filter_obj.id], record[filter_obj.field]
            ):
                passes_all_filters = False
                break

        if passes_all_filters:
            filtered_records.append(record)

    return filtered_records
