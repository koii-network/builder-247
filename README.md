# 247 Builder

## Developing locally

Set up a virtual environment and activate it:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

run tests:

```sh
python3 -m pytest tests/
```

## Developing in Docker

Build the image:

```sh
docker build -t test-builder .
```

Run the container with a mounted volume:

```sh
docker run -it -v $(pwd):/app test-builder
```

This will give you access to your files within the container and run the container in interactive mode with shell access. You can then run tests inside the container using:

```sh
python -m pytest tests/
```

or

```sh
python3 -m pytest tests/
```

To exit the container's shell:

```sh
exit
```
