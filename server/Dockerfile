# Use Node.js 21 as the base image
FROM node:21

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

RUN npm run build

# Copy webasm_bincode_deserializer to dist
RUN cp -r src/webasm_bincode_deserializer dist/

# Clean up src directory
RUN rm -rf src

# Run the web service on container startup.
CMD [ "node", "dist/index.js" ]
