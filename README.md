# 🏓 42-ft_transcandance

## 📌 Overview

`42-ft_transcendance` is a a web-based Pong game where you can challenge friends, chat with them in real-time, and be notified of game events in real-time!

On the backend, we’re using **Django** to handle user authentication, matchmaking and live chat, while in the **frontend**, we focus on implementing responsive design and handling the game’s real-time rendering, ensuring a smooth and immersive experience across all devices. The game itself is built to be simple but exciting, with real-time chat and notifications made possible by **WebSockets** and **Django channels**.

To keep everything organized and easy to deploy, each part of the project — the frontend, backend, database and redis (for channel layer) runs in its own **Docker container**. This makes it easy to scale and maintain as the project grows.

## 🎮 Features

- **User Authentication:** JWT-based authentication for secure login and user sessions.
- **Real-Time Features:** Live chat and notifications using WebSockets and Django Channels.
- **Responsive Frontend:** Built with vanilla JavaScript, ensuring a seamless experience across various devices.
- **Game Features:** Classic Pong game, where users can play against each other.
- **Containers:** Each service (frontend, backend, database, redis) runs in its own Docker container.
- **Monitoring**: Real-time resource monitoring.

## 🛠️ Technologies Used

- 🎨 **Frontend:**
  - Vanilla JavaScript
  - HTML5, CSS3 and SCSS
  - Bootstrap

- 🔧 **Backend:**
  - Python Django (Django REST Framework for the API and Django Channels for Websocket support)
  - PostgreSQL Database
  - Redis (for Channel Layer)
  - JWT (JSON Web Tokens) for user authentication

- 📈 **Monitoring:**
  - Grafana (for visualizing metrics)
  - Prometheus (for collecting metrics)

## 📋 Requirements
- Docker
- Docker Compose

  Follow these steps to download Docker and Docker Compose:
  
  ```bash
  curl -o script.sh https://get.docker.com/
  chmod +x script.sh
  ./script.sh
  rm script.sh
  ```

## 🚀 Usage

### 1️⃣ Clone the repository
  
```bash
git clone https://github.com/osajide/42-ft_transcendence.git
cd 42-ft_transcendence
```

### 2️⃣ Launch
```bash
make
```

### 3️⃣ Access the application

Open your browser and navigate to:

```bash
https://localhost
```
  ❗️ Note: Since a self-signed certificate is used, your browser may show a security warning. You can safely proceed.

### 4️⃣ Monitoring Resources

If you want to monitor the system's resources (e.g., CPU, memory, network usage), you can access the monitoring dashboard at:

```bash
https://localhost/grafana/
```
When accessing Grafana, you will be prompted to log in. Use `admin` for both username and password.
You will be asked to change the password after the first login.

---




Enjoy the game! 🎮✨
