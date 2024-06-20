from datetime import datetime
from casefy import snakecase, titlecase

class BaseSort:
    def __init__(self, field, label=None, is_default=False):
        self.field = field
        self.label = label
        self.is_default = is_default
        self.reverse = False
        class_name = snakecase(self.__class__.__name__)
        self.id = f"{field}_{class_name}"

    def get_sort_key(self):
        # ensure none's be at last always
        if self.reverse:
            none_value = (0,)
        else:
            none_value = (3,)

        def sorting_key(item):
            key = self.field
            value = item.get(key)

            if value is None:
                return none_value
            # ascending => ints, str, none
            # descending => str, ints, none
            # Return a tuple with type indicator and value
            return (1, value) if isinstance(value, int) else (2, value)

        return sorting_key

    def apply(self, data: list):
        return sorted(data, key=self.get_sort_key(), reverse=self.reverse)

    def apply_in_place(self, data: list):
        data.sort(key=self.get_sort_key(), reverse=self.reverse)

    def to_json(self):
        return {
            "id": self.id,
            "label": self.label or self.get_label(),
        }

    def get_label(self):
        raise NotImplementedError


class NumericAscendingSort(BaseSort):
    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- Low to High"


class NumericDescendingSort(BaseSort):
    def __init__(self, field, label=None, is_default=False):

        super().__init__(field, label,is_default)
        self.reverse = True  # For descending order

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- High to Low"


class TrueFirstSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            value = item.get(self.field)
            return 0 if value is True else 1 if value is False else 2

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results With {title_cased_field} First"


class FalseFirstSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            value = item.get(self.field)
            return 0 if value is False else 1 if value is True else 2

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results Without {title_cased_field} First"


class TruthyFirstSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            return not bool(item.get(self.field))

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results With {title_cased_field} First"


class FalsyFirstSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            return bool(item.get(self.field))

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results Without {title_cased_field} First"


class NullsFirstSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            return 0 if item.get(self.field) is None else 1

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results Without {title_cased_field} First"


class NullsLastSort(BaseSort):
    def get_sort_key(self):
        def sorting_key(item):
            return 1 if item.get(self.field) is None else 0

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"Results With {title_cased_field} First"


class _DateSort(BaseSort):
    def __init__(self, field, label=None, date_format=None, is_default=False):
        super().__init__(field, label,is_default)
        self.date_format = date_format

    def parse_date(self, date_str):
        if self.date_format:
            date_obj = datetime.strptime(date_str, self.date_format)
        else:
            date_obj = datetime.fromisoformat(date_str)
        return date_obj

    def get_sort_key(self):
        def sorting_key(item):
            date_str = item.get(self.field)
            if date_str is not None:
                try:
                    date_obj = self.parse_date(date_str)
                    # prevents naive and not naive comparision errors
                    # prioritize dates, then any values
                    return (0, -date_obj.timestamp())  # Valid dates are prioritized
                except (ValueError, TypeError):
                    pass
            return (1,)  # Non-date or None values come last

        return sorting_key


class NewestDateFirstSort(_DateSort):
    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- Newest First"


class OldestDateFirstSort(_DateSort):
    def get_sort_key(self):
        def sorting_key(item):
            date_str = item.get(self.field)
            if date_str is not None:
                try:
                    date_obj = self.parse_date(date_str)
                    # prevents naive and not naive comparision errors
                    # prioritize dates, then any values
                    return (0, date_obj.timestamp())
                except (ValueError, TypeError):
                    pass
            return (1,)

        return sorting_key

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- Oldest First"


class AlphabeticAscendingSort(BaseSort):
    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- A to Z"


class AlphabeticDescendingSort(BaseSort):
    def __init__(self, field, label=None, is_default=False):
        super().__init__(field, label,is_default)
        self.reverse = True  # Z to A

    def get_label(self):
        title_cased_field = titlecase(self.field)
        return f"{title_cased_field} -- Z to A"


class Sort(BaseSort):
    def __init__(self, label, sorts=[], is_default=False):
        # Since Sort does not use a single field, we pass None to BaseSort's field parameter.
        super().__init__(None, label, is_default)
        self.sorts = sorts
        self.is_default = is_default
        
        class_name = snakecase(self.__class__.__name__)
        label_cased = snakecase(label)

        self.id = f"{label_cased}_{class_name}"

    def apply(self, data):
        for sort in self.sorts:
            sort.apply(data)

def apply_sorts(data, sort_data, sort_objects):
    if not sort_data:
        return data

    # Iterate through sort_objects to find a match
    for s in sort_objects:
        if s.id == sort_data:
            s.apply_in_place(data)
            break  # Exit the loop once a matching sort is found

    return data

# python -m 
if __name__ == "__main__":
    c = NumericAscendingSort("age")

    print(c.apply([{"age": 30}, {"age": 20}, {"age": 10}]))