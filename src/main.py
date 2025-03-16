import sys
from shell.shell import Shell

def main():
    shell = Shell()
    try:
        shell.start()
    except KeyboardInterrupt:
        print("\nExiting shell...")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()