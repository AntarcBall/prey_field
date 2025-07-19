- **직관적인 GUI 커스터마이징**:
    
    - **다크/라이트 모드 전환**: 클릭 한 번으로 눈이 편안한 테마를 선택할 수 있습니다.
        
    - **폰트 크기 조절**: "글씨 작게/크게" 버튼을 통해 누구나 자신에게 맞는 가독성을 확보할 수 있습니다.

- **설정(Parameters)의 외부 분리**: 폰트 크기, 테마, Gemini 모델 버전, 각종 배치 사이즈 등 애플리케이션의 주요 동작 방식을 결정하는 변수들을 `config.json` 파일로 분리했습니다. 덕분에 코드 수정 없이 설정 파일만 변경하여 프로그램의 동작을 쉽게 커스터마이징할 수 있으며, 기본값을 하드코딩해두어 설정 파일이 없을 때도 에러 없이 실행되는 안정성을 확보했습니다.
    
- **체계적인 모듈화 (관심사 분리)**: **GUI (`main.py`)**, **YouTube API 핸들러 (`youtube_helper.py`)**, **Gemini API 핸들러 (`gemini_helper.py`)**, **파일 처리 (`file_helper.py`)** 로직을 `utils` 폴더를 기준으로 명확하게 분리했습니다. 이는 코드의 가독성을 높이고 각 기능의 독립적인 수정 및 테스트를 용이하게 하여 유지보수 효율을 극대화합니다.


파이썬 안정적인 파일 경로 참조 가이드: "내 컴퓨터에선 됐는데..." 문제 해결하기1. 무엇이 문제인가? "현재 작업 디렉토리"의 함정파이썬으로 파일을 다룰 때 가장 흔하게 만나는 오류는 FileNotFoundError 입니다. 이 오류의 주된 원인은 상대 경로와 **현재 작업 디렉토리 (Current Working Directory, CWD)**의 동작 방식을 오해하기 때문입니다.스크립트 위치: .py 파일이 실제로 저장된 폴더.현재 작업 디렉토리 (CWD): 터미널이나 IDE에서 스크립트를 실행하는 시점의 폴더 위치.대부분의 개발자는 이 두 가지가 항상 같을 것이라고 가정하지만, 이는 매우 위험한 가정입니다.잘못된 코드 예시 (불안정한 상대 경로)다음과 같은 폴더 구조를 가정해 보겠습니다.my_project/
├── main.py
└── data.json
```main.py` 파일의 코드가 아래와 같다고 해봅시다.

```python
# ⛔️ 잘못된 방식: 불안정한 상대 경로
import json

try:
    with open('./data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("파일 읽기 성공!")
        print(data)
except FileNotFoundError:
    print("오류: data.json 파일을 찾을 수 없습니다!")
my_project 폴더에서 실행하면 성공합니다. (CWD == 스크립트 위치)my_project의 상위 폴더나 전혀 다른 폴더에서 실행하면 실패합니다. (CWD != 스크립트 위치)이처럼 실행 위치에 따라 결과가 달라지는 코드는 절대 좋은 코드가 아닙니다.2. 해결책: 스크립트 위치를 기준으로 절대 경로 만들기해결책은 **"현재 작업 디렉토리가 어디든 상관없이, 항상 스크립트 파일이 있는 위치를 기준으로 파일 경로를 계산"**하는 것입니다. 파이썬의 내장 모듈인 os를 사용하면 이 문제를 간단하게 해결할 수 있습니다.핵심 코드 "공식"import os

# 1. 현재 파일(스크립트)의 절대 경로를 얻는다.
# __file__ 은 현재 실행 중인 스크립트 파일을 의미합니다.
script_path = os.path.abspath(__file__)

# 2. 위 경로에서 파일 이름을 제외한 디렉토리(폴더) 경로를 얻는다.
script_dir = os.path.dirname(script_path)

# 3. 디렉토리 경로와 원하는 파일 이름을 합쳐 최종 파일 경로를 만든다.
# os.path.join() 은 운영체제(Windows, macOS, Linux)에 맞는 경로 구분자(\ 또는 /)를 알아서 사용해줍니다.
target_file_path = os.path.join(script_dir, 'data.json')

print(f"스크립트 폴더: {script_dir}")
print(f"목표 파일 경로: {target_file_path}")
올바른 코드 예시 (안정적인 경로 참조)위 "공식"을 적용하여 코드를 수정해 보겠습니다.# ✅ 올바른 방식: 스크립트 위치 기준 절대 경로
import os
import json

# 스크립트의 디렉토리 경로를 계산
script_dir = os.path.dirname(os.path.abspath(__file__))
# 목표 파일의 전체 경로를 생성
file_path = os.path.join(script_dir, 'data.json')

try:
    # 계산된 절대 경로를 사용
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("파일 읽기 성공!")
        print(data)
except FileNotFoundError:
    print(f"오류: {file_path} 에서 파일을 찾을 수 없습니다!")
except json.JSONDecodeError:
    print(f"오류: {file_path} 파일의 형식이 올바르지 않습니다.")
이제 이 main.py 파일은 컴퓨터의 어느 위치에서 실행해도 항상 자신과 같은 폴더에 있는 data.json 파일을 정확하게 찾아냅니다.3. 더 나은 방법: pathlib 사용하기 (Python 3.4+)Python 3.4 버전부터는 경로를 객체로 다루는 pathlib 모듈이 표준 라이브러리로 추가되었습니다. os.path보다 더 직관적이고 현대적인 코드를 작성할 수 있습니다.pathlib을 사용한 예시# ✨ 더 현대적인 방식: pathlib 사용
from pathlib import Path
import json

# 현재 스크립트 파일의 경로를 Path 객체로 만듭니다.
script_path = Path(__file__)
# .parent 속성을 이용해 부모 디렉토리(폴더)를 가져옵니다.
script_dir = script_path.parent
# / 연산자를 사용해 직관적으로 경로를 결합합니다.
file_path = script_dir / 'data.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("파일 읽기 성공!")
        print(data)
except FileNotFoundError:
    print(f"오류: {file_path} 에서 파일을 찾을 수 없습니다!")
except json.JSONDecodeError:
    print(f"오류: {file_path} 파일의 형식이 올바르지 않습니다.")
```os.path.join` 대신 `/` 연산자를 사용하여 코드가 훨씬 간결하고 읽기 쉬워진 것을 볼 수 있습니다. 특별한 이유가 없다면 `pathlib` 사용을 적극 권장합니다.

---

## 4. 핵심 요약: Do & Don't

| ✅ Do (이렇게 하세요)                                       | ❌ Don't (이렇게 하지 마세요)                               |
| ---------------------------------------------------------- | ----------------------------------------------------------- |
| **스크립트 위치 기준**으로 경로를 만드세요. (`pathlib` 또는 `os.path`) | 단순 상대 경로 (`'./file.txt'`)를 사용하지 마세요.          |
| `os.path.join()` 또는 `pathlib`의 `/` 연산자로 경로를 결합하세요. | 문자열 더하기(`+`)로 경로를 만들지 마세요. (OS 호환성 문제) |
| `try...except FileNotFoundError`로 **파일이 없을 경우**를 항상 대비하세요. | 파일이 항상 존재할 것이라고 가정하지 마세요.                |
| **절대 경로를 하드코딩**하지 마세요. (`'C:/Users/MyPC/project/...'`) |                                                             |

이 원칙들을 따르면 여러분의 코드는 다른 사람의 컴퓨터에서도, 혹은 미래의 내가 다른 환경에서 실행하더라도 문제없이 동작하는 **견고하고 이식성 높은 코드**가 될 것입니다.
