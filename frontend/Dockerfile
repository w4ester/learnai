# Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* .npmrc* ./
RUN npm init -y >/dev/null 2>&1 || true
COPY . ./
ARG VITE_API_BASE=/
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm install && npm run build

# Serve
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
