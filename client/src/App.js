import "./App.css";
import { WebSocketChat } from "./WebSocketClient";

function App() {
	return (
		<div className="App">
			<header className="App-header">
				<WebSocketChat />
			</header>
		</div>
	);
}

export default App;
