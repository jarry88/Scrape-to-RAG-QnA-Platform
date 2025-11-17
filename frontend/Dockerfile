# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port React runs on
EXPOSE 3000

# The command to start the development server
CMD ["npm", "start"]