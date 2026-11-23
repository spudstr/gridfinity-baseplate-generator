# Contributing

Thanks for helping improve the Gridfinity Baseplate Generator.

## Reporting bugs and ideas

- **Bugs**: open an issue with the **Bug report** form. Include the exact
  command you ran, the output it printed, and, for fit problems, what you
  measured on the printed part.
- **Ideas**: open an issue with the **Feature request** form.
- **Security problems**: do not open a public issue. Follow
  [SECURITY.md](SECURITY.md).

## Making changes

1. Fork the repository and create a branch from `main`, named for the
   change, e.g. `feature/magnet-holes` or `fix/corner-gap`.
2. Keep the script **dependency-free**: standard-library Python 3.9+ only.
3. Keep standard output at **standard Gridfinity dimensions** (42 mm grid,
   4.65 mm socket profile) unless the user asks otherwise with an option.
4. Run the tests before opening a pull request:

   ```bash
   python -m unittest discover -s tests -v
   ```

5. If you change the generated geometry, regenerate the example STLs in
   `output/` and mention it in the pull request.
6. Open a pull request into `main` and fill in the template. Automated tests
   run on Windows, macOS and Linux, and must pass before merging.

## Commit messages

Write a short summary line in the imperative ("Add magnet holes", not
"Added magnet holes"), followed by a blank line and a short explanation of
why the change is needed.

## Licensing

By contributing, you agree that your contribution is released under the
project's [MIT License](LICENSE). Do not submit code, CAD or STL files
copied from other projects unless their license allows it and you note the
source in [NOTICE.md](NOTICE.md).
