# ----- 1단계: 빌드 (BUILD STAGE) -----
FROM node:20-alpine AS build
WORKDIR /app

# 라이브러리 설치 (캐싱)
COPY package*.json ./
RUN npm install

# 소스 코드 전체 복사 및 빌드
COPY . .
# Vite 기반 React 프로젝트를 빌드합니다 (dist 폴더 생성)
RUN npm run build


# ----- 2단계: 실행 (PRODUCTION STAGE) -----
FROM nginx:stable-alpine

# 위에서 만든 설정 파일을 Nginx 설정 폴더로 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 1단계(build)에서 빌드된 결과물(dist)만 Nginx의 웹 폴더로 복사
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx의 기본 포트인 80번을 노출합니다.
EXPOSE 80

# Nginx 실행 (백그라운드에서 죽지 않게 설정)
CMD ["nginx", "-g", "daemon off;"]