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

Install project in editable mode:

```sh
pip install -e .
```

Run tests:

```sh
python3 -m pytest tests/
```

Run the agent:

```sh
python3 builder/main.py
```

## Developing in Docker

### Running the Flask Server

Build the image:

```sh
docker build -t test-builder ./builder
```

Run the container:

```sh
docker run test-builder
```

You can also run with a mounted volume if you'd like to change files without updating the container:

```sh
docker run -v $(pwd):/app test-builder
```

### Running Interactively (using the shell)

Change this line in the Dockerfile:

```sh
CMD ["python", "main.py"]
```

to

```sh
CMD ["/bin/bash"]
```

Build the image:

```sh
docker build -t test-builder ./builder
```

Run the container with a mounted volume:

```sh
docker run -it -v $(pwd)/builder:/app test-builder
```

This will give you access to your files within the container and run the container in interactive mode with shell access. You can then run tests inside the container using:

```sh
python -m pytest tests/
```

or

```sh
python3 -m pytest tests/
```

You can also run the flask server in the container with:

```sh
python main.py
```

To exit the container's shell:

```sh
exit
```
