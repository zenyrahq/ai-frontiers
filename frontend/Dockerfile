# Frontend Dockerfile - Simple Production Build
# Next.js 前端应用

FROM node:20-alpine

WORKDIR /app

# Build argument for API URL
ARG NEXT_PUBLIC_API_URL=/api

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build application
RUN npm run build

# Expose port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start application
CMD ["npm", "start"]
