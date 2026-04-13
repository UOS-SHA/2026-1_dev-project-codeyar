import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import ExamListPage from "./pages/ExamListPage";
import ExamPage from "./pages/ExamPage";
import ProblemPage from "./pages/ProblemPage";
import ResultPage from "./pages/ResultPage";
import AdminPage from "./pages/AdminPage";
import SubmissionPage from "./pages/SubmissionPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/student/exams" element={<ExamList />} />
        <Route path="/student/exams/:examId" element={<Exam />} />
        <Route
          path="/student/exams/:examId/problems/:problemId"
          element={<Problem />}
        />
        <Route path="/student/result" element={<Result />} />
        <Route path="/student/submissions" element={<SubmissionPage />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;