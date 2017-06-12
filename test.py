import stripper


def load_test():
    return open("test.txt", "r").read()

def test_stripper():
    text = load_test()
    s = stripper.WikiStripper()
    print(s(text))


def test_stripper_en():
    unicodes = [(0x20, 0x7e)]
    text = load_test()
    s = stripper.WikiStripper(valid_unicodes=unicodes)
    print(s(text))


if __name__ == "__main__":
    test_stripper()
    test_stripper_en()
