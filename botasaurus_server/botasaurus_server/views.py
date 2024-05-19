from casefy import snakecase
import inspect

class Field:
    def __init__(self, key, output_key=None, map=None):
        self.key = key
        self.output_key = output_key or key
        if map and not callable(map):
            raise ValueError(f"map function must be callable for Field '{self.key}'")
        self.map = map

class CustomField:
    def __init__(self, key, map):
        self.key = key
        if not callable(map):
            raise ValueError(
                f"map function must be callable for CustomField '{self.key}'"
            )
        self.output_key = key
        self.map = map

class ExpandDictField:
    def __init__(self, key, fields):
        self.key = key
        self.fields = fields
        for field in fields:
            if not isinstance(field, (Field, CustomField)):
                raise ValueError(
                    f"ExpandDictField '{self.key}' can only contain Field and CustomField"
                )


class ExpandListField:
    def __init__(self, key, fields):
        self.key = key
        self.fields = fields
        for field in fields:
            if not isinstance(field, (Field, CustomField, ExpandDictField)):
                raise ValueError(
                    f"ExpandListField '{self.key}' can only contain Field, CustomField and ExpandDictField"
                )

class View:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.id = snakecase(name)

        expand_list_count = 0
        for field in self.fields:
            if isinstance(field, ExpandListField):
                expand_list_count += 1

        if expand_list_count > 1:
            raise ValueError(
                f"View '{self.name}' can only contain a maximum of one ExpandListField"
            )

        for field in fields:
            if isinstance(field, Field) and field.map:
                if len(inspect.signature(field.map).parameters) != 2:
                    raise ValueError(
                        f"Field '{field.key}' map function must accept 2 arguments"
                    )
            elif isinstance(field, CustomField) and field.map:
                if len(inspect.signature(field.map).parameters) != 1:
                    raise ValueError(
                        f"CustomField '{field.key}' map function must accept 1 argument"
                    )
            elif isinstance(field, ExpandDictField):
                for field in field.fields:
                    if isinstance(field, Field) and field.map:
                        if len(inspect.signature(field.map).parameters) != 3:
                            raise ValueError(
                                f"Field '{field.key}' map function must accept 3 arguments"
                            )
                    elif isinstance(field, CustomField) and field.map:
                        if len(inspect.signature(field.map).parameters) != 2:
                            raise ValueError(
                                f"CustomField '{field.key}' map function must accept 2 argument"
                            )
            elif isinstance(field, ExpandListField):
                for field in field.fields:
                    if isinstance(field, Field) and field.map:
                        if len(inspect.signature(field.map).parameters) != 3:
                            raise ValueError(
                                f"Field '{field.key}' map function must accept 3 arguments"
                            )
                    elif isinstance(field, CustomField) and field.map:
                        if len(inspect.signature(field.map).parameters) != 2:
                            raise ValueError(
                                f"CustomField '{field.key}' map function must accept 2 argument"
                            )
                    elif isinstance(field, ExpandDictField):
                        for field in field.fields:
                            if isinstance(field, Field) and field.map:
                                if len(inspect.signature(field.map).parameters) != 4:
                                    raise ValueError(
                                        f"Field '{field.key}' map function must accept 4 arguments"
                                    )
                            elif isinstance(field, CustomField) and field.map:
                                if len(inspect.signature(field.map).parameters) != 3:
                                    raise ValueError(
                                        f"CustomField '{field.key}' map function must accept 3 argument"
                                    )


    def to_json(self):
        flat_fields = self._flatten_fields(self.fields)
        return {
            "id": self.id,
            "label": self.name,
            "fields": flat_fields
        }

    def _flatten_fields(self, fields):
        flat_list = []
        for field in fields:
            if isinstance(field, (Field, CustomField)):
                # Wrap field.key in a dict with a 'key' attribute
                flat_list.append({"key": field.output_key,})
            elif isinstance(field, (ExpandDictField, ExpandListField)):
                # Only add nested fields without adding the key of the ExpandDictField or ExpandListField itself
                flat_list.extend(self._flatten_fields(field.fields))
        return flat_list


def created_nested_field_values(record, field):
    nested_dict = record.get(field.key, {})  # Use .get() for safer access
    nested_field_values = {}
    for nested_field in field.fields:
        value = nested_dict.get(nested_field.key)  # Use .get() for safer access

        if isinstance(nested_field, Field):
            processed_value = (
                nested_field.map(value, nested_dict, record)
                if nested_field.map
                else value
            )
        elif isinstance(nested_field, CustomField):
            processed_value = nested_field.map(nested_dict, record)

        nested_field_values[nested_field.output_key] = processed_value
    return nested_field_values


def created_nested_field_values_listed(item, field, parent_record):
    nested_dict = item.get(field.key, {})  # Use .get() for safer access
    nested_field_values = {}
    for nested_field in field.fields:
        value = nested_dict.get(nested_field.key)  # Use .get() for safer access

        if isinstance(nested_field, Field):
            processed_value = (
                nested_field.map(value, nested_dict, item, parent_record)
                if nested_field.map
                else value
            )
        elif isinstance(nested_field, CustomField):
            processed_value = nested_field.map(nested_dict, item, parent_record)

        nested_field_values[nested_field.output_key] = processed_value
    return nested_field_values


def perform_apply_view(results: list, view_obj:View):

    processed_results = []
    for record in results:
        expanded_records = [{}]
        for field in view_obj.fields:
            if isinstance(field, Field):
                value = record.get(field.key)  # Use .get() for safer access
                result = field.map(value, record) if field.map else value
                for expanded_record in expanded_records:
                    expanded_record[field.output_key] = result
            elif isinstance(field, CustomField):
                result = field.map(record)
                for expanded_record in expanded_records:
                    expanded_record[field.output_key] = result
            elif isinstance(field, ExpandDictField):
                nested_field_values = created_nested_field_values(record, field)

                for expanded_record in expanded_records:
                    expanded_record.update(nested_field_values)
            elif isinstance(field, ExpandListField):
                nested_list = record.get(field.key, [])  # Use .get() with default [] for safer access
                new_expanded_records = []

                for item in nested_list:
                    for base_expanded_record in expanded_records:
                        new_record = base_expanded_record.copy()
                        for nested_field in field.fields:
                            if isinstance(nested_field, Field):
                                value = item.get(nested_field.key)  # Use .get() for safer access
                                if nested_field.map:
                                    # Field within a list, call map with 3 arguments: value, list_item, record
                                    new_record[nested_field.output_key] = (
                                        nested_field.map(value, item, record)
                                    )
                                else:
                                    new_record[nested_field.output_key] = value

                            elif isinstance(nested_field, CustomField):
                                new_record[nested_field.output_key] = nested_field.map(
                                    item, record
                                )

                            elif isinstance(nested_field, ExpandDictField):
                                nested_field_values = (
                                    created_nested_field_values_listed(
                                        item, nested_field, record
                                    )
                                )
                                new_record.update(nested_field_values)

                        new_expanded_records.append(new_record)

                expanded_records = new_expanded_records
        processed_results.extend(expanded_records)
    return processed_results

def apply_view(results:list, view:str, views):
    if not view:
        return results
    # Iterate through sort_objects to find a match
    for v in views:
        if v.id == view:
            return perform_apply_view(results, v)

    return results