# Boilerplate for a Python project

## How to use it

### Managing requirements

We are going to use [`pip-tools`](https://github.com/jazzband/pip-tools) for managing
requirements.  This means that you should define your project dependencies
in `requirements.in` (pin them to specific version!) and run `make requirements`
to generate `requirements.txt`, which you can then use with `pip install`.

Some useful development dependencies are already defined in `requirements.dev.in`.
Feel free to extend and update them as needed.

### Checking your code

Once you installed the development requirements, you'll be able to set up
[`pre-commit`](https://pre-commit.com) to clean up and check your code
for some common mistakes:

```shell
$ pre-commit install
```

### Testing

Use [`pytest`](https://pytest.org) for testing: put your tests in the `tests/`
directory, define fixtures in `conftest.py`, and finally run `make test`.
