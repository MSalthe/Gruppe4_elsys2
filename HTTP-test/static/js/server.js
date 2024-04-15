const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const net = require('net');

const httpServer = http.createServer((req, res) => {
    if (req.url === '/') {
        fs.readFile('./index.html', (error, content) => {
            if (error) {
                res.writeHead(500);
                res.end('Error loading index.html');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content, 'utf-8');
        });
    }
});

const wss = new WebSocket.Server({ server: httpServer });

wss.on('connection', (ws) => {
    console.log('WebSocket connection established');

    // Relay messages received from the Python client via TCP to web clients over WebSocket
    global.sendDataToClients = (data) => {
        ws.send(data);
    };
});

const tcpServer = net.createServer((socket) => {
    console.log('Python client connected');
    socket.on('data', (data) => {
        console.log('Data received:', data.toString());
        sendDataToClients(data.toString()); // Send this data to all connected WebSocket clients
    });
});

tcpServer.listen(3000, () => console.log('TCP Server listening for Python client on port 3000'));
httpServer.listen(8080, () => console.log('HTTP Server running on http://localhost:8080'));