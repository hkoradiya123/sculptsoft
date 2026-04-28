# SSC Cricket Management System

Mobile-first Progressive Web App (PWA) for SSC cricket operations.

## Features

- JWT authentication with roles (`ADMIN`, `PLAYER`)
- Player management (add/edit/delete/list)
- Payment engine (`MONTHLY` INR 1000, `MATCH` INR 200)
- Match management with paid/unpaid validation
- Strict ball-by-ball event scoring with undo-last support
- Live scoring updates with Socket.io
- Analytics dashboard (revenue, top players, strike rate)
- Installable PWA with offline-ready caching

## Tech Stack

- Frontend: React + Vite, Tailwind CSS, React Router, Zustand, Socket.io-client, Recharts, Workbox via `vite-plugin-pwa`
- Backend: Node.js, Express, MongoDB + Mongoose, Socket.io, JWT, Zod validation
- Deployment targets: Vercel (frontend), Render (backend), MongoDB Atlas

## Project Structure

- `frontend` React PWA app
- `backend` Express API + scoring engine

## Backend Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Fill MongoDB Atlas connection and JWT secret
3. Run:

```bash
cd backend
npm install
npm run dev
```

API base URL: `http://localhost:5000/api`

## Frontend Setup

1. Copy `frontend/.env.example` to `frontend/.env`
2. Set `VITE_API_URL` to your backend API URL
3. Run:

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

PWA production build:

```bash
npm run build
npm run preview
```

## Core API Endpoints

### Auth

- `POST /api/login`

### Players

- `GET /api/players`
- `POST /api/players`
- `PUT /api/players/:id`
- `DELETE /api/players/:id`

### Payments

- `GET /api/payments`
- `POST /api/payments`

### Matches

- `POST /api/matches`
- `GET /api/matches`
- `GET /api/matches/:id/score`

### Scoring

- `POST /api/matches/:id/ball`
- `DELETE /api/matches/:id/ball/last`

### Analytics

- `GET /api/analytics`

## Scoring Rules Implemented

- Stores each ball as immutable event
- Wide/No-ball: +1 base run and not legal delivery
- No-ball triggers next ball free-hit
- Free-hit wicket restriction: only runout allowed
- Bye/Leg-bye count as legal balls and extras
- Strike rotates on odd total runs of a delivery
- Strike rotates at over completion (6 legal balls)
- Match over completion by legal deliveries (`overs * 6`)

## Deployment Notes

### Backend (Render)

- Root directory: `backend`
- Start command: `npm start`
- Environment variables from `backend/.env.example`

### Frontend (Vercel)

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Env var: `VITE_API_URL`
