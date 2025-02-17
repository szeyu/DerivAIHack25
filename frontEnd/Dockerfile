FROM node:18-alpine

# Set the working directory for your frontend code
WORKDIR /frontend

# Copy package files and install dependencies - https://github.com/npm/cli/issues/4828
COPY package*.json ./
COPY node_modules ./node_modules
RUN rm -rf node_modules && rm -rf package-lock.json && npm cache clean --force
RUN npm install

# Copy the rest of your React source code
COPY . .

# Expose the port that your dev server runs on 
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev"]
