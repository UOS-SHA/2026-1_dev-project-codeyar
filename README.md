# Backend (Judge0 및 API 관련 서버)

이 폴더는 프로젝트의 백엔드(Judge0 포함) 및 관련 파이썬 모듈이 위치하는 곳입니다.
최신 Linux 환경 정책(PEP 668)에 따라 파이썬 패키지를 시스템에 직접 설치하는 것이 제한되어 있으므로, 반드시 **가상 환경(venv)**을 사용하여 의존성을 관리해야 합니다.

---

## 🚀 빠른 시작 (팀원용 가이드)

### 1. 가상 환경 생성 (최초 1회)
터미널에서 `Backend` 폴더로 이동한 후 가상 환경을 생성합니다.

```bash
cd Backend
python3 -m venv venv
```

### 2. 가상 환경 활성화
작업(개발, 서버 실행 등)을 시작하기 전에는 항상 가상 환경을 켜주세요.

```bash
# Linux / macOS
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate
```
> **Tip:** 프로젝트 루트 기준 `.vscode` 설정이 배포되어 있으므로, VS Code를 재시작하고 터미널을 열면 자동으로 `(venv)`가 활성화됩니다.

### 3. 패키지 자동 설치
가상 환경이 켜진 상태에서, 담당자가 준비해둔 `requirements.txt`로 필요한 모든 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

이후로는 가상 환경이 켜진 상태(`(venv)`)에서 파이썬 코드를 실행하시면 됩니다.

---

## 🛠 관리자 및 프로세스 기록

Judge0와 통신하기 위한 고민, 설정 과정의 트러블슈팅 등은 세부 파일로 기록되어 있습니다. 구조나 동작 과정이 궁금하시다면 아래 파일을 참고해 주세요:
- `Process_of_judge0.txt`
