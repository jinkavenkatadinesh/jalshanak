# Stage 1: Build the React application
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies first (leverages Docker layer cache)
COPY package*.json ./
RUN npm install

# Copy source assets
COPY . .

# Compile Vite distribution assets
RUN npm run build

# Stage 2: Serve compiled assets using Nginx
FROM nginx:alpine

# Copy static assets from compile step
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx routing config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose web server port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
