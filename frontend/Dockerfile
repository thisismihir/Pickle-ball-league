# Build stage - Frontend is static, so we just need to serve it
FROM node:18-alpine as builder

WORKDIR /app

# Copy all frontend files
COPY . .

# No build step needed for static files, but you can add minification/optimization here if needed
# For now, we just prepare the files

# Production stage - Use nginx to serve static files
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy frontend files to nginx web root
COPY --from=builder /app /usr/share/nginx/html

# Expose port 80 (HTTP)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
