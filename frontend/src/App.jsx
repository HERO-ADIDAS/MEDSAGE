import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import PatientInfo from "./pages/PatientInfo";
import Chat from "./pages/Chat";
import Summary from "./pages/Summary";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/patient-info" element={<PatientInfo />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/summary" element={<Summary />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
