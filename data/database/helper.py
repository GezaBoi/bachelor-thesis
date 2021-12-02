def update_row(row, values: dict):
    for key, value in values.items():
        setattr(row, key, value)
    return row
