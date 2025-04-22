# Use Node.js 20 as the base image
FROM node:20

# Install Yarn globally; Yarn seems to be pre-installed in Node.js 20
# RUN npm install -g yarn

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and yarn.lock (if available)
COPY package*.json ./
COPY yarn.lock ./

# Install dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

RUN yarn build

EXPOSE 3000

# Run the web service on container startup.
CMD [ "node", "dist/src/index.js" ]
