import { BrowserRouter, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./Dashboard";
import { LandingPage } from "./LandingPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}
