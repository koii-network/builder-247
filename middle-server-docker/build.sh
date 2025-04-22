# This should be run from the root directory
cd summarizer/classification-orca/orca-agent
./build.sh
cd ../../../
cd middle-server-docker
docker compose build

