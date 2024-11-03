# Assists

[![PyPI - Version](https://img.shields.io/pypi/v/assists.svg)](https://pypi.org/project/assists)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/assists.svg)](https://pypi.org/project/assists)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

Using pipx:

```console
pipx install assists
```

Using pip:

```console
pip install assists
```

## Terraform command

The new `ast terraform` command that was added in version 0.2.0 was added to provide the ability to install Terraform
that is associated with a specific project. The Terraform versions are cached so future runs don't have to download. This tool
leverages the built in Terraform version constraints except for the greater than, but less than option. It only looks for
the `terraform.tf` file to find the Terraform version as recommended by HashiCorp. If you experience any issues or want an enhancement
please submit an issue or a pull request.

## License

`assists` is distributed under the terms of the [Apache](https://github.com/phillipsj/assists/blob/main/LICENSE.txt) license.
