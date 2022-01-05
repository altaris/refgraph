# refgraph

![Python 3](https://img.shields.io/badge/python-3-blue)
![License](https://img.shields.io/github/license/altaris/refgraph)
[![Code style](https://img.shields.io/badge/style-black-black)](https://pypi.org/project/black)

Reference graph for LaTeX projects

## Using the Github action

```yml
- uses: altaris/refgraph@v1
  with:
    directory: src
    # This will glob src/**/*.tex
- uses: actions/upload-artifact@v2
  with:
    name: pdf
    path: graph.gv.pdf
```

## Contributing

### Dependencies

* `python3.8` or newer;
* `requirements.txt` for runtime dependencies;
* `requirements.dev.txt` for development dependencies.
* `make` (optional);

Simply run
```sh
virtualenv venv -p python3.8
. ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### Documentation

Simply run
```sh
make docs
```
This will generate the HTML doc of the project, and the index file should be at
`docs/index.html`. To have it directly in your browser, run
```sh
make docs-browser
```

### Code quality

Don't forget to run
```sh
make
```
to format the code following [black](https://pypi.org/project/black/),
typecheck it using [mypy](http://mypy-lang.org/), and check it against coding
standards using [pylint](https://pylint.org/).
