
Readme.md
===
도움말

실행 환경
---

아래 조건이 필요합니다.

 - 3dsMax에서 실행되어야 합니다.
 - PyQt4가 3dsMax의 Python을 타겟으로 설치되어야 합니다.
 - 모든 스크립트는 utf-8로 인코딩되어야 합니다.

3dsMax의 Python은 3dsMax 2015 기준으로, 아래 경로에 있습니다.
 
 - C:\Program Files\Autodesk\3ds Max 2015\python

3dsMax의 Python은 기본적으로 2.7(64bit) 버전을 사용합니다. 다른 버전으로 대체하는 것은 테스트되지 않았습니다.


실행
---

원하는 방법을 선택해서 실행합니다.

- 3dsMax의 MAXScript Editor에서, 아래 코드로 실행합니다.
python.ExecuteFile "{PATH_TO_YORICK}\yorick.py"

- Sublime Text 를 사용한다면, Sublime3dsMax 패키지를 이용해서 코드를 즉시 실행할 수 있습니다.
(Sublime3dsMax 패키지는 Package Control을 사용해서 설치할 수 있습니다.)


라이센스
---

PyQt4를 사용하고 있습니다. 반드시 GPL 호환 라이센스로 배포해야 합니다.
http://pyqt.sourceforge.net/Docs/PyQt4/introduction.html#license


---

Maverick Games
===

편의를 위해 dependencies 폴더의 설치파일을 사용하되, 외부에 배포할 경우에는 dependencies 폴더는 포함시키지 않습니다.
