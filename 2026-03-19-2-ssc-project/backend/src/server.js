require('dotenv').config();
const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');

const { connectDB } = require('./config/db');
const User = require('./models/User');

const authRoutes = require('./routes/auth');
const playerRoutes = require('./routes/players');
const paymentRoutes = require('./routes/payments');
const matchRoutes = require('./routes/matches');
const scoringRoutes = require('./routes/scoring');
const analyticsRoutes = require('./routes/analytics');

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_URL || '*',
    credentials: true
  }
});

io.on('connection', (socket) => {
  socket.on('score:join', (matchId) => {
    socket.join(String(matchId));
  });
});

app.use(cors({ origin: process.env.CLIENT_URL || '*', credentials: true }));
app.use(express.json({ limit: '2mb' }));

app.use((req, res, next) => {
  req.io = io;
  next();
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api', authRoutes);
app.use('/api', playerRoutes);
app.use('/api', paymentRoutes);
app.use('/api', matchRoutes);
app.use('/api', scoringRoutes);
app.use('/api', analyticsRoutes);

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal server error', error: err.message });
});

async function bootstrap() {
  await connectDB(process.env.MONGO_URI);

  const adminEmail = process.env.ADMIN_EMAIL;
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (adminEmail && adminPassword) {
    const existing = await User.findOne({ email: adminEmail.toLowerCase() });
    if (!existing) {
      await User.create({
        email: adminEmail.toLowerCase(),
        password: adminPassword,
        role: 'ADMIN'
      });
      console.log('Default admin user created');
    }
  }

  const port = process.env.PORT || 5000;
  server.listen(port, () => {
    console.log(`SSC backend listening on ${port}`);
  });
}

bootstrap().catch((error) => {
  console.error(error);
  process.exit(1);
});
