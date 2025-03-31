# 247 Builder

## Developing locally

Navigate to the correct directory:

```sh
cd builder/container
```

Set up a virtual environment and activate it:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Run tests:

```sh
python3 -m pytest tests/
```

Run the agent:

```sh
python3 main.py
```

## Developing in Docker

### Running the Flask Server

Navigate to the correct directory:

```sh
cd builder/container
```

Build the image:

```sh
docker build -t builder247 .
```

Run the container:

```sh
docker run builder247
```

You can also run with a mounted volume if you'd like to change files without updating the container:

```sh
docker run -v $(pwd):/app builder247
```

### Running Interactively (using the shell)

Navigate to the correct directory:

```sh
cd builder/container
```

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
docker build -t builder247.
```

Run the container with a mounted volume:

```sh
docker run -it -v $(pwd)/builder:/app builder247
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
