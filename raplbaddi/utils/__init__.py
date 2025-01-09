def make_fields_set_only_once(doc, fields, is_only_once=True):
    for fieldname in fields:
        for field in doc.meta.fields:
            if field.fieldname == fieldname:
                field.set_only_once = is_only_once