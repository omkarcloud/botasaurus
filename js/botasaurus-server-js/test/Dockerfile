# You can use this Dockerfile to run the tests on Linux,
# since the sockets behave a little differently there than on Mac
#
# Usage:
# > docker build .
# > docker run <CONTAINER_ID>

FROM node:10

COPY .. /home/node/

RUN npm --quiet set progress=false \
 && npm install --only=prod --no-optional \
 && echo "Installed NPM packages:" \
 && npm list || true \
 && echo "Node.js version:" \
 && node --version \
 && echo "NPM version:" \
 && npm --version

CMD cd /home/node && npm test
