from click import command, option


@command(context_settings={"help_option_names": ["-h", "--help"]}, help="Say hello")
@option("-n", "--name", default="World", help="Name", show_default=True)
def main(name: str = "World"):
    """
    Say hello to the given name.

    Args:
      name: the name to be greeted
    """
    print(f"Hello {name}!")


if __name__ == "__main__":
    main()
