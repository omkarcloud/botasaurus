from casefy import snakecase
import inspect

class Field:
    def __init__(self, key, output_key=None, map=None, show_if=None):
        self.key = key
        self.output_key = output_key or key
        self.show_if = show_if

        if map and not callable(map):
            raise ValueError(f"map function must be callable for Field '{self.key}'")
        self.map = map

class CustomField:
    def __init__(self, key, map, show_if=None):
        self.key = key
        if not callable(map):
            raise ValueError(
                f"map function must be callable for CustomField '{self.key}'"
            )
        self.output_key = key
        self.map = map
        self.show_if = show_if

class ExpandDictField:
    def __init__(self, key, fields, show_if=None):
        self.key = key
        self.fields = fields
        self.show_if = show_if

        for field in fields:
            if not isinstance(field, (Field, CustomField)):
                raise ValueError(
                    f"ExpandDictField '{self.key}' can only contain Field and CustomField"
                )


class ExpandListField:
    def __init__(self, key, fields, show_if=None):
        self.key = key
        self.fields = fields
        self.show_if = show_if
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


    def apply(self, data: list):
        return perform_apply_view(data, self) 

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
        if isinstance(nested_dict, dict):
            value = nested_dict.get(nested_field.key)  # Use .get() for safer access
            if isinstance(nested_field, Field):
                processed_value = (
                    nested_field.map(value, nested_dict, record)
                    if nested_field.map
                    else value
                )
            elif isinstance(nested_field, CustomField):
                processed_value = nested_field.map(nested_dict, record)
        else:
            processed_value = None
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
def get_fields(fields, input_data, hidden_fields):
            ls = []
            for f in fields:
                # Check if instance is Field or CustomField
                if isinstance(f, (Field, CustomField)):
                    if f.show_if:
                        if f.show_if(input_data):
                            ls.append(f)
                        else:
                            hidden_fields.append(f.output_key)
                    else: 
                        ls.append(f)
                # Check if instance is ExpandDictField
                elif isinstance(f, ExpandDictField):
                    if f.show_if:
                        if f.show_if(input_data):
                            ls.append(ExpandDictField(f.key, fields=get_fields(f.fields, input_data, hidden_fields)))
                        else:
                            for i in f.fields:
                                hidden_fields.append(i.output_key)
                    else: 
                        ls.append(ExpandDictField(f.key, fields=get_fields(f.fields, input_data, hidden_fields)))
                # Check if instance is ExpandListField
                elif isinstance(f, ExpandListField):
                    if f.show_if:
                        if f.show_if(input_data):
                            ls.append(ExpandListField(f.key, fields=get_fields(f.fields, input_data, hidden_fields)))
                        else:
                            for i in f.fields:
                                # Corrected the condition to check the instance of i instead of f
                                if isinstance(i, (Field, CustomField)):
                                    hidden_fields.append(i.output_key)
                                else: 
                                    for n in i.fields:  # Assuming i has a fields attribute
                                        hidden_fields.append(n.output_key)
                    else: 
                        ls.append(ExpandListField(f.key, fields=get_fields(f.fields, input_data, hidden_fields)))
            return ls
def perform_apply_view(results: list, view_obj:View, input_data):


    if input_data is not None:
        hidden_fields = []
        target_fields = get_fields(view_obj.fields, input_data, hidden_fields)
    else: 
        hidden_fields = []
        target_fields = view_obj.fields
    processed_results = []
    for record in results:
        expanded_records = [{}]
        
        for field in target_fields:
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
    return processed_results,hidden_fields

def _apply_view_for_ui(results:list, view:str, views, input_data):
    if not view:
        return results, []
    # Iterate through sort_objects to find a match
    for v in views:
        if v.id == view:
            return perform_apply_view(results, v, input_data)

def apply_view(results:list, view:str, views,):
    if not view:
        return results
    # Iterate through sort_objects to find a match
    for v in views:
        if v.id == view:
            return perform_apply_view(results, v, None)[0]