import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/sidebar";
import Topbar from "./components/toolbar";

import Dashboard from "./pages/dashboard";
import Explorer from "./pages/explorer";
import LiveMonitor from "./pages/livemonitor";
import Analytics from "./pages/analytics";
import AIAssistant from "./pages/aiassistant";

function App() {

    return (

        <BrowserRouter>

            <div style={{ display: "flex", height: "100vh" }}>

                <Sidebar />

                <div style={{ flex: 1 }}>

                    <Topbar />

                    <div
                        style={{
                            padding: 25,
                            height: "calc(100vh - 70px)",
                            overflowY: "auto",
                            background: "#f4f6f8"
                        }}
                    >

                        <Routes>

                            <Route path="/" element={<Dashboard />} />
                            <Route path="/live" element={<LiveMonitor />} />
                            <Route path="/explorer" element={<Explorer />} />
                            <Route path="/analytics" element={<Analytics />} />
                            <Route path="/ai" element={<AIAssistant />} />

                        </Routes>

                    </div>

                </div>

            </div>

        </BrowserRouter>

    );

}

export default App;