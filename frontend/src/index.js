import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Chart from "./Charts";

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path='/react-charts' element={<Chart />} />
            </Routes>
        </Router>
    )
}

const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(<App />);