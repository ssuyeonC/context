# Context

워크스페이스 간 공유되는 컨텍스트 파일 저장소입니다.

## 구조

```
.context/
├── inputs/       # 분석 자료, 참고 문서
├── outputs/
│   ├── jira/     # 지라 티켓 요구사항 정리
│   └── proposals/ # 제안서
├── templates/    # 템플릿 양식
├── notes.md      # 메모
└── todos.md      # 할 일
```

## 다른 컴퓨터에서 최초 설정하기

### 1. 기존 .context 파일 백업

```bash
cd /path/to/your-workspace
mv .context .context-backup
```

### 2. 이 repo를 .context로 clone

```bash
git clone https://github.com/ssuyeonC/context.git .context
```

### 3. 기존 파일 병합 (백업한 파일이 있는 경우)

동일한 파일명이 다른 경로에 있을 수 있으므로, 병합 전에 중복 파일을 확인합니다.

```bash
# 중복 파일 확인 (같은 파일명이 다른 경로에 있는지)
diff <(cd .context-backup && find . -type f -not -path './.git/*' | xargs -I{} basename {} | sort) \
     <(cd .context && find . -type f -not -path './.git/*' | xargs -I{} basename {} | sort)

# 병합 (-n: 이미 존재하는 파일은 덮어쓰지 않음)
rsync -a --ignore-existing .context-backup/ .context/

# 변경사항 확인 후 push
cd .context
git add .
git commit -m "merge: add files from other workspace"
git push
```

> **주의**: `rsync --ignore-existing`은 같은 경로의 파일은 덮어쓰지 않습니다.
> 같은 파일명이 다른 경로에 있으면 양쪽 다 남게 되므로, 수동으로 경로를 통일한 뒤 중복을 삭제해야 합니다.

### 4. 백업 폴더 삭제

```bash
rm -rf .context-backup
```

## 일상 동기화

작업 시작 전에 pull, 작업 후에 push 합니다.

```bash
cd .context

# 상대 컴퓨터 변경분 가져오기
git pull

# 내 변경분 올리기
git add .
git commit -m "sync: update"
git push
```
