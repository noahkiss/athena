FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use npm install for lockfile compatibility across npm versions)
RUN npm install

# Copy application code
COPY . .

# Build the application
RUN npm run build

EXPOSE 3000

# Run the production server
CMD ["node", "./dist/server/entry.mjs"]
