import { useState, useEffect, useCallback, useRef } from "react";

const useWebSocketWithAuth = (url, token) => {
	const [socket, setSocket] = useState(null);
	const [isConnected, setIsConnected] = useState(false);
	const [lastMessage, setLastMessage] = useState(null);
	const pingIntervalRef = useRef(null);

	useEffect(() => {
		if (!url) {
			console.log("WebSocket URL is not provided");
			return;
		}
		if (!token) {
			console.log("Authentication token is not provided");
			return;
		}
		const ws = new WebSocket(`${url}?token=${token}`);

		ws.onopen = () => {
			console.log("WebSocket Connected");
			setIsConnected(true);

			// Start sending pings every 30 seconds
			pingIntervalRef.current = setInterval(() => {
				if (ws.readyState === WebSocket.OPEN) {
					ws.send(
						JSON.stringify({
							payload: { message: "ping" },
							metadata: { sent: true },
						})
					);
				}
			}, 60000);
		};

		ws.onmessage = (event) => {
			console.log("Message from server ", event.data);
			const msgObj = JSON.parse(event.data);
			if (msgObj.payload.message === "ping") {
				// Do nothing
				ws.send(
					JSON.stringify({
						payload: { message: "pong" },
						metadata: { sent: true },
					})
				);
			} else if (msgObj.payload.message === "pong") {
				// Do nothing
			} else {
				setLastMessage(msgObj);
			}
		};

		ws.onclose = () => {
			console.log("WebSocket Disconnected");
			setIsConnected(false);
			clearInterval(pingIntervalRef.current);
		};

		setSocket(ws);

		return () => {
			ws.close();
			clearInterval(pingIntervalRef.current);
		};
	}, [url, token]);

	const sendMessage = useCallback(
		(message) => {
			if (socket && socket.readyState === WebSocket.OPEN) {
				socket.send(JSON.stringify(message));
			} else {
				console.error("WebSocket is not connected");
			}
		},
		[socket]
	);

	const disconnect = () => {
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.close();
		}
	};

	return { isConnected, lastMessage, sendMessage, disconnect };
};

export const WebSocketChat = () => {
	const [authUrl, setAuthUrl] = useState("http://localhost/api/0.0.1/login");
	const [websocketUrl, setWebsocketUrl] = useState(
		"ws://localhost/api/0.0.1/ws"
	);
	const [username, setUsername] = useState("test_user");
	const [password, setPassword] = useState("password");
	const [authToken, setAuthToken] = useState("");
	const [message, setMessage] = useState("");
	const [messages, setMessages] = useState([]);

	const { isConnected, lastMessage, sendMessage, disconnect } =
		useWebSocketWithAuth(websocketUrl, authToken);

	const handleConnect = async () => {
		try {
			setMessages([]);
			const response = await fetch(authUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ username, password }),
			});
			const data = await response.json();
			setAuthToken(data.authToken);
		} catch (error) {
			console.error("Authentication failed:", error);
		}
	};

	const handleSendMessage = useCallback(() => {
		if (message.trim()) {
			const msgObj = {
				payload: { message: message },
				metadata: { sent: true },
			};
			sendMessage(msgObj);
			setMessages((prevMessages) => [...prevMessages, msgObj]);
			setMessage("");
		}
	}, [message, sendMessage]);

	useEffect(() => {
		if (lastMessage) {
			setMessages((prevMessages) => [...prevMessages, lastMessage]);
		}
	}, [lastMessage]);

	return (
		<div style={{ maxWidth: "500px", margin: "0 auto", padding: "20px" }}>
			<div>
				<label htmlFor="authUrl">Auth URL: </label>
				<input
					id="authUrl"
					value={authUrl}
					onChange={(e) => setAuthUrl(e.target.value)}
				/>
			</div>
			<div>
				<label htmlFor="websocketUrl">WebSocket URL: </label>
				<input
					id="websocketUrl"
					value={websocketUrl}
					onChange={(e) => setWebsocketUrl(e.target.value)}
				/>
			</div>
			<div>
				<label htmlFor="username">Username: </label>
				<input
					id="username"
					value={username}
					onChange={(e) => setUsername(e.target.value)}
				/>
			</div>
			<div>
				<label htmlFor="password">Password: </label>
				<input
					id="password"
					type="password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
				/>
			</div>
			<button onClick={handleConnect} disabled={isConnected}>
				Connect
			</button>
			<button onClick={() => disconnect()} disabled={!isConnected}>
				Disconnect
			</button>

			<div style={{ marginTop: "20px" }}>
				<p>Connection status: {isConnected ? "Connected" : "Disconnected"}</p>
				<div
					style={{
						height: "200px",
						overflowY: "auto",
						border: "1px solid #ccc",
						padding: "10px",
						marginBottom: "10px",
					}}
				>
					{messages.map((msg, index) => (
						<div
							key={index}
							style={{
								marginBottom: "5px",
								padding: "5px",
								backgroundColor: msg.metadata?.sent ? "#f0fff0" : "#f0f0ff",
								color: "#000",
							}}
						>
							{msg.payload.message}
						</div>
					))}
				</div>
				<div>
					<textarea
						value={message}
						onChange={(e) => setMessage(e.target.value)}
						multiple
						onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
						style={{ width: "100%", resize: "vertical", minHeight: "50px" }}
					/>
					<button
						onClick={handleSendMessage}
						disabled={!isConnected}
						style={{ width: "28%", marginLeft: "2%" }}
					>
						Send
					</button>
				</div>
			</div>
		</div>
	);
};
