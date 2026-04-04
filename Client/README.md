# 클라이언트 README
## 개요
asdf

## YarClient

## YarDog
YarDog는 사용자의 단축키 입력과 클립보드 감시를 위해 만들어진 프로그램입니다.

명령줄 인자는 다음과 같습니다:
```
필수 명령줄 인자
--student-id: 학생의 학번입니다.
--student-name: 학생의 이름입니다.

기타 명령줄 인자
-p / --policy: 단축키 정책을 담은 파일을 지정합니다.
-l / --log-level: 로그를 출력하는 정도를 지정합니다. 값으로는 quiet, default, talkative, verbose가 가능하며, 기본값은 default입니다.
-w / --worker-count: 쓰레드 풀에 담을 쓰레드의 수를 지정합니다. 1과 10 사이의 값입니다.
```

예시는 아래와 같습니다.
```bash
YarDog.exe -p policy.txt -l verbose --student-id 2023123456 --student-name 신시호
YarDog.exe --policy policy.txt --log-level verbose --student-id 2023123456 --student-name 신시호 --worker-count 5
```

YarDog이 파싱하는 policy 파일의 구조는 다음과 같습니다.

* +, -, 또는 !로 시작합니다. 각각 허용, 비허용, 특수 동작을 의미합니다.
    * 허용된 단축키는 전혀 기록되지 않습니다.
    * 비허용된 단축키는 항상 기록됩니다.
    * 특수 동작은 아래에서 설명합니다.
* 이후에는 콤마로 구분된 단축키가 나옵니다. 예를 들면 "CTRL, C" 등입니다.
    * 이때, '*' 문자로 모든 키를 지정할 수 있습니다.
* 마지막에는 '$'로 시작하는 문자열이 올 수 있습니다. 이 문자열은 로그에 기록 및 전송됩니다.
    * 특수 동작일 경우, '$'의 뒤에는 항상 GUID가 따라옵니다.
```
+CTRL, C    # Ctrl + C의 조합을 허용합니다.
!CTRL, V, $846cf704-6728-4b16-99a1-6e514c362845    # 특수 단축키입니다.
-ALT, TAB, $ALT + TAB    # Alt + Tab을 허용하지 않습니다.
-WIN, *, $Windows!    # Win + 모든 키를 허용하지 않습니다.
```

Policy 파일은 프로그램에 의해 로드되어 Trie(트라이) 구조로 정리됩니다.