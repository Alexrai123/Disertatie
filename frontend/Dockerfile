# Frontend Dockerfile
# References:
# - see docs/13_app_arch.txt §5 Deployment (Docker-ready)
# - see docs/03_non_func_req.txt §7 Portability (Docker)

# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install
COPY frontend ./
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
