def make_selection(max: int) -> int:
    selection = input('#: ')
    num = None
    try:
        num = int(selection)
    except:
        return None
    if num < 1 or num > max:
        return None
    return num