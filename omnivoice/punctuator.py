"""
OmniVoice - Smart Punctuation & Comprehensive IT Entity Enhancer
Restores grammatical punctuation (commas, sentence capitalization, boundary periods)
and normalizes developer terminology to standard Latin casings.
Zero emojis.
"""

import re
from typing import List, Tuple

# Ordered list of regex replacements (multi-word and plurals first!)
DEV_TERMS: List[Tuple[str, str]] = [
    # Multi-word compound terms
    (r"\bдокер\s*компо[уз](?:[а-я]{1,3})?\b", "Docker Compose"),
    (r"\bпулл?\s*реквест(?:ы|ах|ам|ами|ов)\b", "Pull Requests"),
    (r"\bпулл?\s*реквест(?:[а-я]{1,3})?|пр\b", "Pull Request"),
    (r"\bпуш\s*ту\s*то[л]?к\b", "Push-to-Talk"),
    (r"\bрест\s*апи\b", "REST API"),
    (r"\bкод\s*ревью\b", "code review"),
    (r"\bюнит\s*тест(?:ы|ах|ам|ами|ов)\b", "unit tests"),
    (r"\bюнит\s*тест(?:[а-я]{1,3})?\b", "unit test"),
    (r"\bтест\s*кейс(?:ы|ах|ам|ами|ов)|тесткейс(?:ы|ах|ам|ами|ов)\b", "test cases"),
    (r"\bтест\s*кейс(?:[а-я]{1,3})?|тесткейс(?:[а-я]{1,3})?\b", "test case"),
    (r"\bси\s*плюс\s*плюс\b", "C++"),
    (r"\bси\s*шарп\b", "C#"),
    (r"\bмак\s*ос|макос\b", "macOS"),
    (r"\bчат\s*гпт|чатгпт\b", "ChatGPT"),
    (r"\bхаггинг\s*фейс\b", "Hugging Face"),
    (r"\bдокер\s*файл(?:[а-я]{1,3})?|докерфайл(?:[а-я]{1,3})?\b", "Dockerfile"),
    (r"\bси\s*ай\s*\/?\s*си\s*ди|сиай\s*сиди\b", "CI/CD"),
    (r"\bопен\s*сорс\b", "open source"),
    (r"\bфулл?\s*стек(?:[а-я]{1,3})?\b", "fullstack"),
    (r"\bвеб\s*ассембли|васм\b", "WebAssembly"),
    (r"\bвиспер\s*смо[л]?\b", "Whisper Small"),
    (r"\bвиспер\s*турбо\b", "Whisper Turbo"),
    (r"\bгугл\s*спич\b", "Google Speech"),
    (r"\bветк(?:а|у|е|ой)\s*дев\b", "ветку dev"),
    (r"\bветк(?:а|у|е|ой)\s*мейн\b", "ветку main"),
    (r"\bветк(?:а|у|е|ой)\s*мастер\b", "ветку master"),

    # Operating Systems & Environments
    (r"\bюникс(?:[а-я]{1,3})?\b", "Unix"),
    (r"\bлинукс(?:[а-я]{1,3})?\b", "Linux"),
    (r"\bубунт[а-я]{1,2}\b", "Ubuntu"),
    (r"\bдебиан(?:[а-я]{1,3})?\b", "Debian"),
    (r"\bарч(?:[а-я]{1,3})?\b", "Arch Linux"),
    (r"\bвиндовс(?:[а-я]{1,3})?|винду|винде|винда|виндой\b", "Windows"),
    (r"\bвсл\b", "WSL"),

    # AI Coding Agents & LLM Tools
    (r"\bантигравити\b", "Antigravity"),
    (r"\bклоди[яею]|клод(?:[а-я]{1,3})?\b", "Claude"),
    (r"\bкодекс(?:[а-я]{1,3})?\b", "Codex"),
    (r"\bэйдер(?:[а-я]{1,3})?|айдер(?:[а-я]{1,3})?\b", "Aider"),
    (r"\bкурсор(?:[а-я]{1,3})?\b", "Cursor"),
    (r"\bоллам[а-я]{1,2}\b", "Ollama"),
    (r"\bлам[а-я]{1,2}|ллам[а-я]{1,2}\b", "Llama"),
    (r"\bмистрал[ь|я|ем|ю]\b", "Mistral"),
    (r"\bдипсик(?:[а-я]{1,3})?\b", "DeepSeek"),
    (r"\bгемини|джеминай\b", "Gemini"),
    (r"\bгпт|джипити\b", "GPT"),
    (r"\bллм|лски\b", "LLM"),
    (r"\bвиспер(?:[а-я]{1,3})?\b", "Whisper"),

    # Plural dev entities (must come before singular)
    (r"\bвебсокет(?:ы|ах|ам|ами|ов)\b", "WebSockets"),
    (r"\bвебсокет(?:[а-я]{1,3})?\b", "WebSocket"),
    (r"\bэндпоинт(?:ы|ах|ам|ами|ов)\b", "endpoints"),
    (r"\bэндпоинт(?:[а-я]{1,3})?\b", "endpoint"),
    (r"\bвебхук(?:и|ах|ам|ами|ов)\b", "webhooks"),
    (r"\bвебхук(?:[а-я]{1,3})?\b", "webhook"),
    (r"\bкоммит(?:ы|ах|ам|ами|ов)\b", "commits"),
    (r"\bзакоммить|коммит(?:[а-я]{1,3})?\b", "commit"),
    (r"\bбранч(?:и|ах|ам|ами|ей)\b", "branches"),
    (r"\bбранч(?:[а-я]{1,3})?\b", "branch"),

    # Version Control & Git
    (r"\bгит(?:[а-я]{1,3})?\b", "Git"),
    (r"\bгитхаб(?:[а-я]{1,3})?\b", "GitHub"),
    (r"\bгитлаб(?:[а-я]{1,3})?\b", "GitLab"),
    (r"\bзапушь|пушить|запушить\b", "push"),
    (r"\bспулли|пуллить|спуллить\b", "pull"),
    (r"\bмердж(?:[а-я]{1,3})?|смерджи|мерджить|смерджить\b", "merge"),
    (r"\bребейз(?:[а-я]{1,3})?|сребейзи|ребейзить\b", "rebase"),
    (r"\bстэш(?:[а-я]{1,3})?|стеш(?:[а-я]{1,3})?|застеши\b", "stash"),
    (r"\bчекаут(?:[а-я]{1,3})?|зачекаути\b", "checkout"),
    (r"\bклон(?:[а-я]{1,3})?|склонируй\b", "clone"),
    (r"\bрепо\b", "repo"),

    # Languages, Runtimes & Frameworks
    (r"\bпайтон(?:[а-я]{1,3})?|питон(?:[а-я]{1,3})?\b", "Python"),
    (r"\bджаваскрипт(?:[а-я]{1,3})?|жс\b", "JavaScript"),
    (r"\bтайпскрипт(?:[а-я]{1,3})?|тс\b", "TypeScript"),
    (r"\bнод[ауе]|нод\s*жс\b", "Node.js"),
    (r"\bраст(?:[а-я]{1,3})?\b", "Rust"),
    (r"\bголанг(?:[а-я]{1,3})?\b", "Go"),
    (r"\bбаш(?:[а-я]{1,3})?\b", "bash"),
    (r"\bзш\b", "zsh"),
    (r"\bфастапи|фаст\s*апи\b", "FastAPI"),
    (r"\bфласк(?:[а-я]{1,3})?\b", "Flask"),
    (r"\bджанго\b", "Django"),
    (r"\bреакт(?:[а-я]{1,3})?\b", "React"),
    (r"\bнекст\s*жс|некст\b", "Next.js"),
    (r"\bпайторч(?:[а-я]{1,3})?|торч(?:[а-я]{1,3})?\b", "PyTorch"),
    (r"\bтензорфлоу\b", "TensorFlow"),

    # Containers, Databases & Cloud Infra
    (r"\bдокер(?:[а-я]{1,3})?\b", "Docker"),
    (r"\bкубер(?:нетес)?(?:[а-я]{1,3})?\b", "Kubernetes"),
    (r"\bнжинкс(?:[а-я]{1,3})?|энжинкс(?:[а-я]{1,3})?\b", "NGINX"),
    (r"\bредис(?:[а-я]{1,3})?\b", "Redis"),
    (r"\bпостгрес(?:[а-я]{1,3})?|постгре\b", "PostgreSQL"),
    (r"\bмонго|монгодб\b", "MongoDB"),
    (r"\bмускул|майскюэль\b", "MySQL"),
    (r"\bскюэль|эскьюэль\b", "SQL"),
    (r"\bкликхаус(?:[а-я]{1,3})?\b", "ClickHouse"),
    (r"\bкафк[а-я]{1,2}\b", "Kafka"),
    (r"\bреббит(?:[а-я]{1,3})?|рэббит(?:[а-я]{1,3})?|рэббит\s*эмкью\b", "RabbitMQ"),
    (r"\bселери\b", "Celery"),
    (r"\bтераформ(?:[а-я]{1,3})?\b", "Terraform"),
    (r"\bансибл(?:[а-я]{1,3})?\b", "Ansible"),
    (r"\bавс|амазон\s*веб\s*сервисез\b", "AWS"),
    (r"\bажур(?:[а-я]{1,3})?|эйжур\b", "Azure"),
    (r"\bс3\b", "S3"),
    (r"\bпрометеус|прометей\b", "Prometheus"),
    (r"\bграфан[а-я]{1,2}\b", "Grafana"),

    # Protocols, Web & Architecture
    (r"\bкурл(?:[а-я]{1,3})?\b", "cURL"),
    (r"\bапи|эпиай\b", "API"),
    (r"\bграфкьюэл|графкл\b", "GraphQL"),
    (r"\bджейсон(?:[а-я]{1,3})?|жсон\b", "JSON"),
    (r"\bямл|ямел\b", "YAML"),
    (r"\bхттпс\b", "HTTPS"),
    (r"\bхттп\b", "HTTP"),
    (r"\bгэ\s*эр\s*пэ\s*цэ|джерписи\b", "gRPC"),
    (r"\bпротобуф(?:[а-я]{1,3})?\b", "Protobuf"),
    (r"\bjwt|жвт\b", "JWT"),
    (r"\bоаут|оаус\b", "OAuth"),
    (r"\bфронтенд(?:[а-я]{1,3})?|фронт(?:[а-я]{1,3})?\b", "frontend"),
    (r"\bбэкенд(?:[а-я]{1,3})?|бекенд(?:[а-я]{1,3})?|бэк(?:[а-я]{1,3})?\b", "backend"),
    (r"\bдебаг(?:[а-я]{1,3})?|задебаж[ь|и]\b", "debug"),
    (r"\bбагфикс(?:[а-я]{1,3})?\b", "bugfix"),
    (r"\bрефакторинг(?:[а-я]{1,3})?|порефактори\b", "refactoring"),
    (r"\bдеплой(?:[а-я]{1,3})?|задеплой\b", "deploy"),
    (r"\bцли|кли\b", "CLI"),
    (r"\bттуи|туи\b", "TUI"),
    (r"\bгуи\b", "GUI"),
    (r"\bпту|пти\b", "PTY"),
    (r"\bстдин\b", "stdin"),
    (r"\bстдаут\b", "stdout"),
    (r"\bстдерр\b", "stderr"),
]

CONJUNCTIONS: List[str] = [
    r"\bа\b", r"\bно\b", r"\bчто\b", r"\bчтобы\b", r"\bкак\b",
    r"\bесли\b", r"\bкогда\b", r"\bпотому что\b", r"\bтак как\b",
    r"\bхотя\b", r"\bкоторы[йяехм]+\b", r"\bгде\b", r"\bкуда\b",
    r"\bоткуда\b", r"\bто есть\b", r"\bто бишь\b", r"\bнасколько\b",
    r"\bпоскольку\b", r"\bпричем\b", r"\bа именно\b", r"\bдабы\b",
    r"\bпока\b", r"\bтем более\b"
]

INTRO_WORDS: List[str] = [
    r"\bв общем-то\b", r"\bв общем\b", r"\bкороче говоря\b", r"\bкороче\b",
    r"\bкстати говоря\b", r"\bкстати\b", r"\bпожалуйста\b", r"\bнаверное\b",
    r"\bпожалуй\b", r"\bк слову\b", r"\bсобственно говоря\b", r"\bсобственно\b",
    r"\bпо сути говоря\b", r"\bпо сути\b", r"\bнапример\b", r"\bво-первых\b",
    r"\bво-вторых\b", r"\bв-третьих\b", r"\bв целом\b", r"\bкроме того\b",
    r"\bтак сказать\b", r"\bпо правде говоря\b"
]

SENTENCE_STARTERS = {
    "Я", "Мы", "Ты", "Вы", "Он", "Она", "Оно", "Они",
    "Это", "Этот", "Эта", "Эти", "Твоя", "Твой", "Ваша", "Ваш", "Моя", "Мой", "Наш",
    "Попробуй", "Попробуйте", "Скажи", "Скажите", "Сделай", "Сделайте",
    "Напиши", "Напишите", "Проверь", "Проверьте", "Посмотри", "Посмотрите",
    "Как", "Что", "Где", "Куда", "Когда", "Зачем", "Почему", "Какая", "Какой", "Какие",
    "Но", "Однако", "Если", "Хотя", "Сейчас", "Затем", "Потом", "После",
    "Добавь", "Добавьте", "Удали", "Удалите", "Создай", "Создайте", "Запусти", "Запустите"
}

def enhance_text(text: str) -> str:
    if not text:
        return ""
    res = text.strip()

    # 1. Punctuate introductory words
    for intro in INTRO_WORDS:
        word = intro.replace(r"\b", "")
        res = re.sub(rf"(?i)^{re.escape(word)}\s+", f"{word.capitalize()}, ", res)
        res = re.sub(rf"(?i)\s+{re.escape(word)}\s+", f", {word}, ", res)

    # 2. Insert commas before subordinate and coordinative conjunctions
    for conj in CONJUNCTIONS:
        c = conj.replace(r"\b", "")
        res = re.sub(rf"(?i)(?<![,\.!\?])\s+{re.escape(c)}\b", f", {c}", res)

    # 3. Normalize technical and developer entities
    for pattern, repl in DEV_TERMS:
        res = re.sub(pattern, repl, res, flags=re.IGNORECASE)

    # 4. Restore missing periods before capitalized sentence starters
    words = res.split()
    res_words = []
    for i, w in enumerate(words):
        if i > 0 and w in SENTENCE_STARTERS:
            prev = res_words[-1]
            if not prev.endswith((".", "!", "?", ":", ";", ",")):
                res_words[-1] = prev + "."
        res_words.append(w)
    res = " ".join(res_words)

    # 5. Clean double punctuation and spaces
    res = re.sub(r",\s*,+", ",", res)
    res = re.sub(r"\.\s*\.+", ".", res)
    res = re.sub(r"\s*,\s*", ", ", res)
    res = re.sub(r"\s*\.\s*", ". ", res)
    res = re.sub(r"^,\s*", "", res)

    # 6. Capitalize after sentence ends
    res = re.sub(r"(^|[\.\?!]\s+)([a-zа-яё])", lambda m: m.group(1) + m.group(2).upper(), res)

    # 7. Ensure final punctuation
    res = res.strip()
    if res and not res.endswith((".", "!", "?")):
        res += "."

    return res.strip()
