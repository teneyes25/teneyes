FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
COPY apps/web/package.json apps/web/package.json
RUN npm install

FROM node:22-alpine AS build
WORKDIR /app
ARG NEXT_PUBLIC_DEPLOY_VERSION=local-dev
ENV NEXT_PUBLIC_DEPLOY_VERSION=$NEXT_PUBLIC_DEPLOY_VERSION
COPY --from=deps /app/node_modules ./node_modules
COPY package*.json ./
COPY apps/web ./apps/web
RUN npm run build -w @maejong-intranet/web

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ARG NEXT_PUBLIC_DEPLOY_VERSION=local-dev
ENV NEXT_PUBLIC_DEPLOY_VERSION=$NEXT_PUBLIC_DEPLOY_VERSION
COPY --from=build /app/apps/web/.next/standalone ./
COPY --from=build /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /app/apps/web/public ./apps/web/public
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
