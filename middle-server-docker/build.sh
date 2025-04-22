# This should be run from the root directory
cd summarizer/classification-orca/orca-agent
./build.sh
cd ../../../
cd middle-server-docker
docker compose -f ./middle-server-docker/docker-compose.yml build

