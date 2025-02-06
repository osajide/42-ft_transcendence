# ft_transcandance

## 📌 Overview

`ft_transcendance` is a a web-based Pong game where you can challenge friends, chat with them in real-time, and be notified of game events in real-time!

On the backend, we’re using **Django** to handle user authentication, matchmaking and live chat, while in the **frontend**, we focus on implementing responsive design and handling the game’s real-time rendering, ensuring a smooth and immersive experience across all devices. The game itself is built to be simple but exciting, with real-time chat and notifications made possible by **WebSockets** and **Django channels**.

To keep everything organized and easy to deploy, each part of the project — the frontend, backend, database and redis (for channel layer) runs in its own **Docker container**. This makes it easy to scale and maintain as the project grows.

## Features

- **User Authentication:** JWT-based authentication for secure login and user sessions.
- **Real-Time Features:** Live chat and notifications using WebSockets and Django Channels.
- **Responsive Frontend:** Built with vanilla JavaScript, ensuring a seamless experience across various devices.
- **Game Features:** Classic Pong game, where users can play against each other.
- **Containers:** Each service (frontend, backend, database, redis) runs in its own Docker container.

## Technologies Used

- **Frontend:**
  - Vanilla JavaScript
  - HTML5, CSS3, SCSS
  - Bootstrap

- **Backend:**
  - Python Django (Django REST Framework for the API and Django Channels for Websocket support)
  - PostgreSQL Database
  - Redis (for Channel Layer)
  - JWT (JSON Web Tokens) for user authentication

## Requirements
- Docker
- Docker Compose

## Usage

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/ft_transcandance.git
cd ft_transcandance
```

### 2️⃣ 
