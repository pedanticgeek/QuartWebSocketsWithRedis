# QuartWebSocketsWithRedis

### Summary

This repository contains my example code for a basic setup of Quart API with Quart-Auth, Quart-Redis and Quart-Schema. It includes REST and WebSocket endpoints, where websocket session queues are managed by Redis.

### Why Quart API?

- Build for async
- Built-in Websockets
- Similar to Flask
- Good and simple plugins

### What's included

1. Quart API setup;
2. Basic Schema for Login/Register REST endpoints, and incoming Websocket message;
3. User data model;
4. Basic Error Handler;
5. Basic Websocket session with send/receive/ping-pong;
6. Logger with colors;
7. Docker Compose for the service and Redis;
8. Simple ReactJS client for the Websocket server.

### How to run

#### Single-worker Reload mode

- used for development
- runs a single worker
- monitors changes and reloads the service
  `docker compose up`

#### Multi-worker mode

- used to run on multiple (4) workers in parallel
- demonstrates why we need Redis for messages queue and can't just use AsyncIO queues
  `MODE=prod docker compose up`

#### ReactJS client

This client is the most basic tool for Websocket connection. It authenticates using username and password, then establishes a websocket connection with the provided Auth token.

```
cd client
npm install
npm start
```

### Thanks

Big thanks to the Pallets Projects and Quart team (quart.palletsprojects.com). Please consider contributing and/or sponsoring the project (https://github.com/pallets/quart).
