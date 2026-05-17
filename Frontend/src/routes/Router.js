import { BrowserRouter, Routes, Route } from "react-router-dom";

import LoginPage from "../pages/auth/LoginPage";
import SignupPage from "../pages/auth/SignupPage";

import StudentMainPage from "../pages/student/StudentMainPage";
import ProfessorMainPage from "../pages/professor/ProfessorMainPage";

import ClassListPage from "../pages/student/ClassListPage";
import ExamPage from "../pages/student/ExamPage";

import ProblemSolvePage from "../pages/student/ProblemSolvePage";
import SubmissionPage from "../pages/student/SubmissionPage";
import ResultPage from "../pages/student/ResultPage";

import ProfessorClassListPage from "../pages/professor/ProfessorClassListPage";
import ExamManagePage from "../pages/professor/ExamManagePage";

import ProblemManagePage from "../pages/professor/ProblemManagePage";
import StudentManagePage from "../pages/professor/StudentManagePage";

import ResultManagePage from "../pages/professor/ResultManagePage";
import CheatingLogPage from "../pages/professor/CheatingLogPage";

function Router() {
  return (
    <BrowserRouter>
      <Routes>

        <Route path="/" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        <Route path="/student/main" element={<StudentMainPage />} />
        <Route path="/professor/main" element={<ProfessorMainPage />} />

        <Route path="/student/classes" element={<ClassListPage />} />
        <Route path="/student/exam" element={<ExamPage />} />

        <Route path="/student/solve" element={<ProblemSolvePage />} />
        <Route path="/student/submission" elemnet={<SubmissionPage />} />
        <Route path="/student/result" element={<ResultPage />} />

        <Route path="/professor/classes" element={<ProfessorClassListPage />} />
        <Route path="/professor/manage" element={<ExamManagePage />} />

        <Route path="/professor/problem" element={<ProblemManagePage />} />
        <Route path="/professor/student" element={<StudentManagePage />} />

        <Route path="/professor/result" element={<ResultManagePage />} />
        <Route path="/professor/log" element={<CheatingLogPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default Router;