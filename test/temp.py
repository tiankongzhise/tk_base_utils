from pathlib import Path

if __name__ == "__main__":
    x = Path(__file__)
    y = Path(x)
    print(f'x is {x},y is {y}')


