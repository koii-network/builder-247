# Use Node.js 21 as the base image
FROM node:21

# Install Yarn globally
RUN npm install -g yarn

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
CMD [ "node", "dist/index.js" ]
