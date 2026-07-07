#!/usr/bin/env python3

def main() -> None:
    try:
        ...
    except ValueError as e:  # Pasar al main
        print(f"Error: {e}")
    except FileNotFoundError:  # Pasar al main # En el main atrapar os error para proteger al open tambien
        print(f"File: {self.route} doesn't exits")    


if __name__ == "__main__":
    main()
