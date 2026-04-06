# -*- coding: utf-8 -*-

import streamlit as st
from openai import OpenAI  # Меняем библиотеку
import re

# Настройка клиента OpenRouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=st.secrets["openrouter_key"],
)

st.set_page_config(page_title="SlovoAnaliz", layout="wide")

# CSS (оставляем без изменений)
st.markdown("""
<style>
.stButton > button {
    background: linear-gradient(135deg, #66b3ff, #4da6ff);
    color: white;
    border-radius: 12px;
    padding: 10px 18px;
    border: none;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(77,166,255,0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4da6ff, #3399ff);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 20px rgba(77,166,255,0.5);
}
.stButton > button:active {
    transform: scale(0.97);
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #66b3ff, #4da6ff);
    color: white;
}
.big-title {
    font-size: 37px;
    font-weight: 700;
    font-family: "Quicksand", sans-serif;
}
.blue {
    background: linear-gradient(135deg, #66b3ff, #4da6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sub-text {
    font-size: 20px;
    font-weight: 600;
    font-family: "Quicksand", sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown("""
<div class="big-title">
    <span class="blue">СЛОВО</span><span class="black">АНАЛИЗ</span>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI анализ текста, оценка и улучшение</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Настройки")

# В OpenRouter названия моделей выглядят иначе, добавил актуальные ID
model_choice = st.sidebar.selectbox(
    "Модель",
    ["openai/gpt-4o-mini"]
)

user_type = st.sidebar.selectbox(
    "Кто вы?",
    ["Школьник", "Студент", "Блогер", "Работа"]
)

# Функция для запроса к OpenRouter
def ask_ai(prompt):
    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": "http://localhost:8501", # Для логов OpenRouter
        "X-Title": "SlovoAnaliz",
      },
      model=model_choice,
      messages=[
        {"role": "user", "content": prompt}
      ]
    )
    return completion.choices[0].message.content

# Совет дня
if st.sidebar.button("Совет дня"):
    with st.sidebar:
        with st.spinner("Загрузка..."):
            tip = ask_ai("Дай короткий совет по улучшению письма")
            st.info(tip)

# История
if "history" not in st.session_state:
    st.session_state.history = []

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    text = st.text_area("Введите текст:", height=200)

    analysis_type = st.radio(
        "Тип анализа",
        ["Грамматика", "Стиль", "Логика", "Полный анализ"]
    )

    words = len(text.split())
    reading_time = round(words / 200, 1) if words else 0

    st.write(f"Слов: {words}")
    st.write(f"Время чтения: {reading_time} мин")

    if st.button("АНАЛИЗИРОВАТЬ"):
        if text.strip() == "":
            st.warning("Введите текст!")
        else:
            prompt = f"""
                Оцени текст строго по критериям.
                Максимум 100 баллов:
                ГРАММАТИКА: 0-25
                СТИЛЬ: 0-25
                ЛОГИКА: 0-25
                СТРУКТУРА: 0-25

                Верни строго:
                ГРАММАТИКА: число
                СТИЛЬ: число
                ЛОГИКА: число
                СТРУКТУРА: число
                ИТОГ: сумма
                ИИ_ВЕРОЯТНОСТЬ: число
                ОШИБКИ:
                - ...
                РЕКОМЕНДАЦИИ:
                - ...
                УЛУЧШЕННЫЙ ТЕКСТ:
                ...

                Текст:
                {text}
                """

            with st.spinner("Анализ..."):
                result = ask_ai(prompt)

                def extract(name):
                    match = re.search(fr"{name}:\s*(\d+)", result)
                    return int(match.group(1)) if match else 0

                total_match = re.search(r"ИТОГ:\s*(\d+)", result)
                st.session_state.score = int(total_match.group(1)) if total_match else 50
                st.session_state.score = max(0, min(100, st.session_state.score))

                st.session_state.ai_prob = extract("ИИ_ВЕРОЯТНОСТЬ")
                st.session_state.grammar = extract("ГРАММАТИКА")
                st.session_state.style = extract("СТИЛЬ")
                st.session_state.logic = extract("ЛОГИКА")
                st.session_state.structure = extract("СТРУКТУРА")

                st.session_state.result = result
                st.session_state.history.append(result)

    if st.button("Улучшить текст"):
        if text.strip():
            with st.spinner("Улучшаем..."):
                better = ask_ai(f"Улучши текст:\n{text}")
                st.subheader("Улучшенный текст")
                st.write(better)

with col2:
    st.markdown("### Результат")

    if "score" in st.session_state:
        st.metric("Оценка", f"{st.session_state.score}/100")
        st.progress(st.session_state.score / 100)

        st.markdown("### Детали")
        c1, c2 = st.columns(2)
        c1.metric("Грамматика", st.session_state.grammar)
        c2.metric("Стиль", st.session_state.style)
        c3, c4 = st.columns(2)
        c3.metric("Логика", st.session_state.logic)
        c4.metric("Структура", st.session_state.structure)

        st.markdown("### Детектор ИИ")
        st.metric("Вероятность ИИ", f"{st.session_state.ai_prob}%")

        if st.session_state.ai_prob > 70:
            st.error("Похоже на AI")
        elif st.session_state.ai_prob > 30:
            st.warning("Есть признаки AI")
        else:
            st.success("Текст человеческий")

    if "result" in st.session_state:
        clean = re.sub(r"(ОЦЕНКА|ИТОГ|ИИ_ВЕРОЯТНОСТЬ|ГРАММАТИКА|СТИЛЬ|ЛОГИКА|СТРУКТУРА):.*?\n", "", st.session_state.result, flags=re.IGNORECASE)
        st.markdown("### Анализ")
        st.write(clean)
        st.download_button("Скачать", data=clean, file_name="analysis.txt")

# История в Sidebar
st.sidebar.title("История")
for i, item in enumerate(st.session_state.history[-5:]):
    st.sidebar.write(f"Анализ {i+1}")

if st.button("Сделать текст более человеческим"):
    if text.strip():
        human_prompt = f"Перепиши текст так, чтобы он звучал максимально естественно, убери шаблонность:\n{text}"
        with st.spinner("Очеловечиваем текст..."):
            humanized = ask_ai(human_prompt)
            st.subheader("Очеловеченный текст:")
            st.write(humanized)