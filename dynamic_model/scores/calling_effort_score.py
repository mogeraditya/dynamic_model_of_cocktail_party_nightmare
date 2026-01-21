def calling_effort(bat_objects):
    number_of_calls = []
    for bat in bat_objects:
        number_of_calls.append(len(bat.emit_times))
    return number_of_calls
