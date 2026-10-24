"""
OmniVoice - Smart Punctuation & IT Entity Enhancer
Restores grammatical punctuation (commas, sentence capitalization, boundary periods) and technical terms.
Zero emojis.
"""

import re

DEV_MAP = {
    # Operating Systems & Environments
    r"\b(юникс[еау]?)\b": "Unix",
    r"\b(линукс[еау]?)\b": "Linux",
    r"\b(убунту)\b": "Ubuntu",
    r"\b(дебиан[еау]?)\b": "Debian",
    r"\b(арч[еау]?)\b": "Arch Linux",
    r"\b(мак\s*ос|макос)\b": "macOS",
    r"\b(виндовс[еау]?|винду|винде|винда)\b": "Windows",
    r"\b(всл)\b": "WSL",

    # AI Coding Agents & LLM Tools
    r"\b(антигравити)\b": "Antigravity",
    r"\b(клоди[яею]|клод[ауе]?)\b": "Claude",
    r"\b(кодекс[еау]?)\b": "Codex",
    r"\b(эйдер[еау]?|айдер[еау]?)\b": "Aider",
    r"\b(курсор[еау]?)\b": "Cursor",
    r"\b(чат\s*гпт|чатгпт)\b": "ChatGPT",
    r"\b(гпт|джипити)\b": "GPT",
    r"\b(ллм|лски)\b": "LLM",
    r"\b(виспер\s*смо[л]?)\b": "Whisper Small",
    r"\b(виспер\s*турбо)\b": "Whisper Turbo",
    r"\b(виспер[еау]?)\b": "Whisper",
    r"\b(гугл\s*спич)\b": "Google Speech",
    r"\b(пуш\s*ту\s*то[л]?к)\b": "Push-to-Talk",
    r"\b(промпт[ауеы]?)\b": "промпт",

    # Version Control & Collaboration
    r"\b(гит[еау]?)\b": "Git",
    r"\b(гитхаб[еау]?)\b": "GitHub",
    r"\b(гитлаб[еау]?)\b": "GitLab",
    r"\b(пулл?\s*реквест[ауе]?|пр)\b": "Pull Request",
    r"\b(пулл?\s*реквесты)\b": "Pull Requests",
    r"\b(мердж[еау]?|смерджи|мерджить)\b": "merge",
    r"\b(коммит[ауе]?|закоммить|коммитить)\b": "commit",
    r"\b(коммиты)\b": "commits",
    r"\b(запушь|пушить)\b": "push",
    r"\b(спулли|пуллить)\b": "pull",
    r"\b(бранч[еау]?)\b": "branch",
    r"\b(репо[еау]?)\b": "repo",
    r"\b(репозитори[йяею]|репозиториев)\b": "репозиторий",
    r"\b(си\s*ай\s*\/?\s*си\s*ди|сиай\s*сиди)\b": "CI/CD",

    # Languages & Frameworks
    r"\b(пайтон[еау]?|питон[еау]?)\b": "Python",
    r"\b(джаваскрипт[еау]?|жс)\b": "JavaScript",
    r"\b(тайпскрипт[еау]?|тс)\b": "TypeScript",
    r"\b(нод[ауе]|нод\s*жс)\b": "Node.js",
    r"\b(раст[еау]?)\b": "Rust",
    r"\b(голанг[еау]?)\b": "Go",
    r"\b(си\s*плюс\s*плюс)\b": "C++",
    r"\b(си\s*шарп)\b": "C#",
    r"\b(баш[еау]?)\b": "bash",
    r"\b(зш)\b": "zsh",
    r"\b(фастапи|фаст\s*апи)\b": "FastAPI",
    r"\b(фласк[еау]?)\b": "Flask",
    r"\b(джанго)\b": "Django",
    r"\b(реакт[еау]?)\b": "React",
    r"\b(некст\s*жс|некст)\b": "Next.js",
    r"\b(вью\s*жс)\b": "Vue.js",

    # Containers, DB & Infra
    r"\b(докер[еау]?)\b": "Docker",
    r"\b(докерфайл[еау]?)\b": "Dockerfile",
    r"\b(докер\s*компо[уз][еау]?)\b": "Docker Compose",
    r"\b(кубер[еау]?|кубернетес[еау]?)\b": "Kubernetes",
    r"\b(нжинкс[еау]?|энжинкс[еау]?)\b": "NGINX",
    r"\b(редис[еау]?)\b": "Redis",
    r"\b(постгрес[еау]?|постгре)\b": "PostgreSQL",
    r"\b(монго|монгодб)\b": "MongoDB",
    r"\b(скюэль|эскьюэль)\b": "SQL",

    # Protocols, Formats & Architecture
    r"\b(апи|эпиай)\b": "API",
    r"\b(рест\s*апи|рест)\b": "REST API",
    r"\b(графкьюэл|графкл)\b": "GraphQL",
    r"\b(эндпоинт[ауе]?)\b": "endpoint",
    r"\b(эндпоинты)\b": "endpoints",
    r"\b(джейсон[еау]?|жсон)\b": "JSON",
    r"\b(ямл|ямел)\b": "YAML",
    r"\b(хттп)\b": "HTTP",
    r"\b(хттпс)\b": "HTTPS",
    r"\b(вебсокет[ауе]?)\b": "WebSocket",
    r"\b(вебсокеты)\b": "WebSockets",
    r"\b(фронтенд[еау]?|фронт[еау]?)\b": "frontend",
    r"\b(бэкенд[еау]?|бекенд[еау]?|бэк[еау]?)\b": "backend",
    r"\b(дебаг[еау]?|задебаж[ь|и])\b": "debug",
    r"\b(багфикс[еау]?)\b": "bugfix",
    r"\b(рефакторинг[еау]?)\b": "refactoring",
    r"\b(код\s*ревью)\b": "code review",
    r"\b(деплой[еау]?|задеплой)\b": "deploy",
    r"\b(тесткейс[ауе]?)\b": "test case",
    r"\b(тесткейсы)\b": "test cases",
    r"\b(юнит\s*тест[ауе]?)\b": "unit test",
    r"\b(юнит\s*тесты)\b": "unit tests",
    r"\b(цли|кли)\b": "CLI",
    r"\b(ттуи|туи)\b": "TUI",
    r"\b(гуи)\b": "GUI",
    r"\b(пту|пти)\b": "PTY",
    r"\b(стдин)\b": "stdin",
    r"\b(стдаут)\b": "stdout",
    r"\b(стдерр)\b": "stderr",
}

CONJUNCTIONS = [
    r"\bа\b", r"\bно\b", r"\bчто\b", r"\bчтобы\b", r"\bкак\b",
    r"\bесли\b", r"\bкогда\b", r"\bпотому что\b", r"\bтак как\b",
    r"\bхотя\b", r"\bкоторы[йяехм]+\b", r"\bгде\b", r"\bкуда\b",
    r"\bоткуда\b", r"\bто есть\b", r"\bто бишь\b", r"\bнасколько\b",
    r"\bпоскольку\b", r"\bпричем\b", r"\bа именно\b", r"\bдабы\b",
    r"\bпока\b"
]

INTRO_WORDS = [
    r"\bв общем-то\b", r"\bв общем\b", r"\bкороче говоря\b", r"\bкороче\b",
    r"\bкстати говоря\b", r"\bкстати\b", r"\bпожалуйста\b", r"\bнаверное\b",
    r"\bпожалуй\b", r"\bк слову\b", r"\bсобственно говоря\b", r"\bсобственно\b",
    r"\bпо сути\b", r"\bнапример\b", r"\bво-первых\b", r"\bво-вторых\b",
    r"\bв-третьих\b", r"\bв целом\b", r"\bкроме того\b"
]

SENTENCE_STARTERS = {
    "Я", "Мы", "Ты", "Вы", "Он", "Она", "Оно", "Они",
    "Это", "Этот", "Эта", "Эти", "Твоя", "Твой", "Ваша", "Ваш", "Моя", "Мой", "Наш",
    "Попробуй", "Попробуйте", "Скажи", "Скажите", "Сделай", "Сделайте",
    "Напиши", "Напишите", "Проверь", "Проверьте", "Посмотри", "Посмотрите",
    "Как", "Что", "Где", "Куда", "Когда", "Зачем", "Почему", "Какая", "Какой", "Какие",
    "Но", "Однако", "Если", "Хотя", "Сейчас", "Затем", "Потом", "После"
}

def enhance_text(text: str) -> str:
    if not text:
        return ""
    res = text.strip()

    # Punctuate introductory words
    for intro in INTRO_WORDS:
        word = intro.replace(r"\b", "")
        res = re.sub(rf"(?i)^{re.escape(word)}\s+", f"{word.capitalize()}, ", res)
        res = re.sub(rf"(?i)\s+{re.escape(word)}\s+", f", {word}, ", res)

    # Insert commas before subordinate conjunctions
    for conj in CONJUNCTIONS:
        c = conj.replace(r"\b", "")
        res = re.sub(rf"(?i)(?<![,\.!\?])\s+{re.escape(c)}\b", f", {c}", res)

    # Normalize technical and developer entities
    for pattern, repl in DEV_MAP.items():
        res = re.sub(pattern, repl, res, flags=re.IGNORECASE)

    # Restore missing periods before capitalized sentence starters
    words = res.split()
    res_words = []
    for i, w in enumerate(words):
        if i > 0 and w in SENTENCE_STARTERS:
            prev = res_words[-1]
            if not prev.endswith((".", "!", "?", ":", ";", ",")):
                res_words[-1] = prev + "."
        res_words.append(w)
    res = " ".join(res_words)

    # Clean double punctuation and spaces
    res = re.sub(r",\s*,+", ",", res)
    res = re.sub(r"\.\s*\.+", ".", res)
    res = re.sub(r"\s*,\s*", ", ", res)
    res = re.sub(r"\s*\.\s*", ". ", res)
    res = re.sub(r"^,\s*", "", res)

    # Capitalize after sentence ends
    res = re.sub(r"(^|[\.\?!]\s+)([a-zа-яё])", lambda m: m.group(1) + m.group(2).upper(), res)

    # Ensure final punctuation
    res = res.strip()
    if res and not res.endswith((".", "!", "?")):
        res += "."

    return res.strip()
