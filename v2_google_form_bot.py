import requests
import random
import time
import json
import os
import copy

# === CONFIGURATION ===
URL = "https://docs.google.com/forms/d/e/1FAIpQLSehIJDYbGUUvTEWOiq6WQQ_eV250l7B4-f8VHz8AGdzxucFoQ/formResponse"
TOTAL_RESPONSES = 104
STATE_FILE = "state.json"

# === OPTIONS (unchanged from your first code) ===
options_map = {
    "entry.457041491": [
        "16 лет и младше",
        "17–18 лет",
        "19–20 лет",
        "21–22 года",
        "23 года и старше"
    ],
    "entry.900081255": ["Мужской", "Женский"],
    "entry.2072137170": [
        "г. Астана", "г. Алматы", "г. Шымкент", "Актюбинская область",
        "Алматинская область", "Атырауская область", "Восточно-Казахстанская область",
        "Западно-Казахстанская область", "Карагандинская область", "Кызылординская область",
        "Павлодарская область", "Северо-Казахстанская область", "Туркестанская область"
    ],
    "entry.1467051264": ["Школа", "Университет / Вуз", "Работа"],
    "entry.2049384046": ["Казахский", "Русский", "Английский", "Смешанный (несколько языков)"],
    "entry.997831765": ["Казахский", "Русский", "Английский"],
    "entry.2016190063": ["Казахский", "Русский", "Английский"],
    "entry.1708145665": ["1", "2", "3", "4", "5"],
    "entry.1452720691": [
        "Сложно понимать специфические термины.",
        "Преподаватель говорит слишком быстро.",
        "Трудно быстро конспектировать и переводить одновременно.",
        "Сложно задавать вопросы или отвечать на занятиях.",
        "Трудностей нет, я всё понимаю."
    ],
    "entry.1794521284": [
        "Ищу перевод или объяснение на родном языке в интернете.",
        "Прошу одногруппников/друзей объяснить на более понятном языке.",
        "Пытаюсь догадаться по смыслу и контексту.",
        "Жду, когда преподаватель объяснит еще раз."
    ],
    "entry.286483656": [
        "Да, постоянно (смешиваю термины из разных языков).",
        "Иногда (когда не хватает слов на одном языке).",
        "Нет, стараюсь использовать только один язык."
    ],
    "entry.737822750": [
        "Да, это значительно облегчает понимание материала.",
        "Немного помогает, но мешает погружению в основной язык обучения.",
        "Нет, это только создает путаницу."
    ],
    "entry.331049506": ["1", "2", "3", "4", "5"],
    "entry.1295596769": [
        "На родном языке (понимание темы происходит быстрее и глубже).",
        "На языке обучения (даже если он не родной, мне проще усваивать академический материал именно на нем).",
        "Смешанно: термины легче понимать на английском/языке обучения, а общую суть — на родном языке.",
        "Разницы нет, я одинаково эффективно воспринимаю информацию на любом из языков."
    ]
}

# === PHRASES FOR THE LAST OPEN QUESTION ===
phrases_by_category = {
    'native': [
        "На родном языке я лучше понимаю сложные концепции, потому что не нужно тратить силы на перевод.",
        "Родной язык позволяет мне быстрее схватывать суть, особенно когда речь идёт о новых терминах.",
        "Мне проще запоминать материал на родном языке, так как он ассоциируется с повседневным общением.",
        "Я могу сосредоточиться на содержании.",
        "Родной язык даёт более глубокое понимание.",
        "Когда материал сложный, я лучше понимаю его на родном языке, это экономит время.",
        "На родном языке меньше когнитивной нагрузки.",
        "Родной язык помогает быстрее вникать в суть.",
        "Лучше запоминаю.",
        "На родном языке могу задать уточняющие вопросы.",
        "Думаю на родном языке, поэтому и понимаю лучше.",
        "Мне легче формулировать мысли на родном.",
        "Родной язык это основа моего мышления.",
        "Я быстрее нахожу ответы, когда думаю на родном языке.",
        "На родном языке информация усваивается естественнее.",
        "Так мне легче анализировать материал.",
        "Родной язык позволяет глубже погружаться в тему.",
        "Мне комфортнее учиться на родном языке.",
        "Понимаю нюансы лучше на родном.",
        "На родном языке я увереннее себя чувствую при обсуждении тем.",
        "Легче конспектировать на родном языке.",
        "Быстрее читаю и понимаю тексты на родном.",
        "Сложные концепции проще разобрать на родном.",
        "На родном языке не устаю так быстро при учёбе.",
        "Легче запоминать определения на родном языке."
    ],
    'learning': [
        "Я привык к терминам на языке обучения, потому что вся литература и лекции на нём.",
        "Мне кажется, что на языке обучения терминология более точная.",
        "Это язык моей будущей профессии, поэтому я стараюсь использовать его для всех учебных материалов.",
        "В интернете и учебниках больше информации на этом языке.",
        "На языке обучения проще обсуждать темы с преподавателями и однокурсниками.",
        "Источники и статьи в основном на этом языке.",
        "Все материалы на этом языке.",
        "Преподаватели требуют использовать термины на языке обучения.",
        "В профессии принято использовать этот язык.",
        "Легче готовиться к экзаменам, если все на одном языке.",
        "Привык так учиться с первого курса.",
        "Терминология на языке обучения звучит точнее.",
        "Так легче искать дополнительные материалы.",
        "Учебники написаны на этом языке, поэтому привык.",
        "На языке обучения есть больше научных статей.",
        "Проще писать курсовые и рефераты на языке обучения.",
        "Лекции ведутся на этом языке, поэтому и мыслю на нём.",
        "Не хочу путать термины при переводе.",
        "На этом языке я изучаю предмет с самого начала.",
        "Так удобнее общаться с однокурсниками.",
        "Весь учебный процесс построен на этом языке.",
        "Мне важно знать термины именно на языке обучения для будущей работы.",
        "На этом языке больше видеолекций и онлайн курсов.",
        "Проще сдавать экзамены, когда учишь на том же языке.",
        "Уже сформировалась привычка."
    ],
    'mixed': [
        "Мне удобно общую идею понимать на родном, а термины запоминать на языке обучения.",
        "Я билингвист.",
        "Сложные вещи легче понимать на родном, но профессиональные термины проще использовать на языке обучения.",
        "Иногда на родном языке лучше понимается общая картина, а детали лучше на языке обучения.",
        "Мозг сам выбирает удобный язык.",
        "Мне удобно переключаться между языками.",
        "Смешиваю языки, потому что так говорят в моем окружении.",
        "Зависит от темы.",
        "Теорию лучше понимаю на родном, а практику на языке обучения.",
        "Использую оба языка, потому что так эффективнее.",
        "Некоторые термины не переводятся, поэтому использую оригинал.",
        "Общую суть схватываю на родном, а детали на языке обучения.",
        "Переключаюсь в зависимости от сложности материала.",
        "На разных предметах удобнее разные языки.",
        "Мне легче объяснить другим на родном, а самому разобраться на языке обучения.",
        "Когда что-то непонятно, перевожу в голове на родной.",
        "Использую тот язык, на котором нашёл объяснение.",
        "Зависит от ситуации.",
        "Привык думать на двух языках одновременно.",
        "Конспекты веду на двух языках.",
        "Термины запоминаю на языке обучения а суть понимаю на родном.",
        "Оба языка для меня равноценны в учёбе.",
        "Так проще запоминать.",
        "Мне кажется это нормально для большинства."
    ],
    'none': [
        "Мне без разницы.",
        "Я легко переключаюсь и не замечаю разницы.",
        "Главное чтобы было понятно.",
        "Нет особых предпочтений, материал усваивается одинаково.",
        "Разницы нет.",
        "Я свободно владею несколькими языками.",
        "Главное - чтобы информация была понятной.",
        "Мне все равно, на каком языке учиться.",
        "Я хорошо понимаю на любом языке.",
        "Для меня язык не имеет значения.",
        "Легко на любом.",
        "Не вижу разницы между языками в плане учёбы.",
        "Понимаю одинаково хорошо на всех языках.",
        "Мне комфортно на любом языке.",
        "Язык не влияет на моё понимание.",
        "Привык к многоязычной среде.",
        "Не замечаю, на каком языке учусь.",
        "Всё равно, лишь бы материал был качественный.",
        "Не испытываю затруднений ни на одном языке.",
        "Информация одинаково хорошо усваивается.",
        "Я вырос в многоязычной семье, поэтому разницы нет.",
        "Могу одинаково эффективно учиться на обоих языках.",
        "Для меня главное содержание, а не язык.",
        "Нет предпочтений."
    ],
    'neutral': [
        "Просто так получилось.",
        "Мне так удобнее.",
        "Не задумывался об этом.",
        "Так сложилось.",
        "Привычка.",
        "Легче усваивать информацию.",
        "Просто так.",
        "Не знаю.",
        "Мне так удобно.",
        "Удобно.",
        "Так привык.",
        "Потому что.",
        "Без понятия.",
        "Легче.",
        "Нравится.",
        "Эффективно.",
        "Так проще.",
        "Не задумывался.",
        "Сложно объяснить.",
        "Думаю это правильно.",
        "Все так делают.",
        "Нзн.",
        "Привык с детства.",
        "Так учили.",
        "Комфортно.",
        "Лучше понимаю.",
        "Меньше ошибок.",
        "Быстрее.",
        "Так получается.",
        "Не могу объяснить почему."
    ]
}

# === GARBAGE PHRASES (unused, kept for reference) ===
garbage_phrases = ["asdasd", "ghbdtn", "z", "ъ", "0"]

# === HELPER FUNCTIONS (from your first code) ===
def format_text_randomly(text):
    """Light random formatting."""
    text = text.strip()
    if random.random() < 0.4 and text:
        text = text[0].lower() + text[1:]
    if text.endswith('.'):
        if len(text) > 1 and random.random() < 0.5:
            text = text[:-1]
        elif len(text) > 1 and random.random() < 0.1:
            text = text[:-1] + "..."
    else:
        if random.random() < 0.3:
            text += "."
    if not text:
        text = "."
    return text

def generate_profile(index):
    """Generate a respondent profile (weights from your first code)."""
    profile = {}

    # Occupation
    occ_weights = [0.10, 0.85, 0.05]  # school, uni, work
    occupation = random.choices(options_map["entry.1467051264"], weights=occ_weights, k=1)[0]
    profile['occupation'] = occupation

    # Age (consistent with occupation)
    age_options = options_map["entry.457041491"]
    if occupation == "Школа":
        age_weights = [0.3, 0.7, 0.0, 0.0, 0.0]
    elif occupation == "Университет / Вуз":
        age_weights = [0.0, 0.3, 0.5, 0.15, 0.05]
    else:  # Работа
        age_weights = [0.0, 0.0, 0.2, 0.3, 0.5]
    profile['age'] = random.choices(age_options, weights=age_weights, k=1)[0]

    # Gender
    profile['gender'] = random.choice(options_map["entry.900081255"])

    # Region
    regions = options_map["entry.2072137170"]
    region_weights = [0.25, 0.35, 0.20] + [0.20/17] * (len(regions)-3)
    profile['region'] = random.choices(regions, weights=region_weights, k=1)[0]

    # Native language (90% Kazakh, 10% Russian as in your first code)
    native_lang = random.choices(["Казахский", "Русский"], weights=[0.9, 0.1], k=1)[0]
    profile['native_lang'] = native_lang

    # School language (depends on native)
    if native_lang == "Казахский":
        school_lang = random.choices(
            ["Казахский", "Русский", "Английский"],
            weights=[0.85, 0.10, 0.05], k=1)[0]
    else:  # Русский
        school_lang = random.choices(
            ["Казахский", "Русский", "Английский"],
            weights=[0.10, 0.85, 0.05], k=1)[0]
    profile['school_lang'] = school_lang

    # University / work language
    if occupation == "Университет / Вуз":
        if native_lang == "Казахский":
            uni_weights = [0.10, 0.10, 0.70, 0.10]
        else:  # Русский
            uni_weights = [0.05, 0.15, 0.70, 0.10]
    elif occupation == "Школа":
        if school_lang == "Казахский":
            uni_weights = [0.70, 0.02, 0.20, 0.08]
        elif school_lang == "Русский":
            uni_weights = [0.02, 0.70, 0.20, 0.08]
        else:  # Английский (rare)
            uni_weights = [0.00, 0.00, 0.95, 0.05]
    else:  # Работа
        uni_weights = [0.30, 0.20, 0.40, 0.10]
    profile['uni_lang'] = random.choices(options_map["entry.2049384046"], weights=uni_weights, k=1)[0]

    return profile

def get_phrase_from_category(cat, categorized, original):
    """Retrieve a phrase from the given category, refilling from original if needed."""
    if categorized.get(cat):
        return categorized[cat].pop(0)
    # Fallback to original (allow repeats)
    if original.get(cat):
        return random.choice(original[cat])
    # Ultimate fallback
    return "."

def generate_one_response(index, categorized, original, dots_left):
    """Generate one complete form response."""
    profile = generate_profile(index)

    data = {"fvv": "1"}

    # Fill answers from profile
    data["entry.457041491"] = profile['age']
    data["entry.900081255"] = profile['gender']
    data["entry.2072137170"] = profile['region']
    data["entry.1467051264"] = profile['occupation']
    data["entry.997831765"] = profile['native_lang']
    data["entry.2016190063"] = profile['school_lang']
    data["entry.2049384046"] = profile['uni_lang']

    native = profile['native_lang']
    uni = profile['uni_lang']
    is_studying_foreign = (uni != native) and (uni != "Смешанный (несколько языков)")

    # 8. Ease of understanding
    if is_studying_foreign:
        understanding_weights = [0.05, 0.15, 0.45, 0.25, 0.10]
    else:
        understanding_weights = [0.0, 0.05, 0.15, 0.40, 0.40]
    data["entry.1708145665"] = random.choices(options_map["entry.1708145665"], weights=understanding_weights, k=1)[0]

    # 9. Difficulties (multiple choice)
    understanding_score = int(data["entry.1708145665"])
    if understanding_score >= 4:
        data["entry.1452720691"] = "Трудностей нет, я всё понимаю."
    else:
        diffs = options_map["entry.1452720691"][:-1]
        chosen_diffs = random.sample(diffs, k=random.randint(1, 2))
        data["entry.1452720691"] = chosen_diffs

    # 10. Action when facing difficulties
    action_weights = [0.45, 0.30, 0.15, 0.10]
    data["entry.1794521284"] = random.choices(options_map["entry.1794521284"], weights=action_weights, k=1)[0]

    # 11. Code‑switching
    if is_studying_foreign or uni == "Смешанный (несколько языков)":
        cs_weights = [0.60, 0.30, 0.10]
    else:
        cs_weights = [0.20, 0.40, 0.40]
    data["entry.286483656"] = random.choices(options_map["entry.286483656"], weights=cs_weights, k=1)[0]

    # 12. Help from switching
    if is_studying_foreign:
        help_weights = [0.65, 0.25, 0.10]
    else:
        help_weights = [0.20, 0.30, 0.50]
    data["entry.737822750"] = random.choices(options_map["entry.737822750"], weights=help_weights, k=1)[0]

    # 13. Mental effort
    if is_studying_foreign:
        effort_weights = [0.05, 0.20, 0.40, 0.25, 0.10]
    else:
        effort_weights = [0.60, 0.20, 0.10, 0.05, 0.05]
    data["entry.331049506"] = random.choices(options_map["entry.331049506"], weights=effort_weights, k=1)[0]

    # 14. Preferred language for complex topics
    if uni == native:
        data["entry.1295596769"] = "На родном языке (понимание темы происходит быстрее и глубже)."
    elif uni == "Смешанный (несколько языков)":
        easier_weights = [0.30, 0.10, 0.50, 0.10]
        data["entry.1295596769"] = random.choices(options_map["entry.1295596769"], weights=easier_weights, k=1)[0]
    else:
        easier_weights = [0.40, 0.15, 0.35, 0.10]
        data["entry.1295596769"] = random.choices(options_map["entry.1295596769"], weights=easier_weights, k=1)[0]

    # 15. Final open answer (with dots and neutral override)
    remaining = TOTAL_RESPONSES - index
    ans = None

    # Dots (exactly 4 across all responses)
    if dots_left > 0 and remaining > 0:
        prob_dot = dots_left / remaining
        if random.random() < prob_dot:
            ans = "."
            dots_left -= 1

    if ans is None:
        # Override: if teaching language is Russian or Kazakh, use neutral
        if profile['uni_lang'] in ("Русский", "Казахский"):
            target_cat = 'neutral'
        else:
            choice_14 = data["entry.1295596769"]
            if "На родном языке" in choice_14:
                target_cat = 'native'
            elif "На языке обучения" in choice_14:
                target_cat = 'learning'
            elif "Смешанно" in choice_14:
                target_cat = 'mixed'
            elif "Разницы нет" in choice_14:
                target_cat = 'none'
            else:
                target_cat = 'neutral'

        ans = get_phrase_from_category(target_cat, categorized, original)
        ans = format_text_randomly(ans)

    if not ans:
        ans = "."
    data["entry.593581296"] = ans
    data["pageHistory"] = "0"

    return data, ans, categorized, dots_left

# === STATE MANAGEMENT ===
def load_state():
    """Load or initialize persistent state."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Initialise categorized pools (shuffled)
        categorized = {}
        for cat, phrases in phrases_by_category.items():
            cat_phrases = phrases.copy()
            random.shuffle(cat_phrases)
            categorized[cat] = cat_phrases

        return {
            'sent_count': 0,
            'categorized': categorized,
            'dots_left': 4
        }

def save_state(state):
    """Save state to file."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# === MAIN (one run) ===
def main():
    state = load_state()
    sent_count = state['sent_count']
    categorized = state['categorized']
    dots_left = state['dots_left']

    if sent_count >= TOTAL_RESPONSES:
        print(f"All {TOTAL_RESPONSES} responses already sent. Exiting.")
        return

    # Reconstruct original pools (constant)
    original = {cat: phrases.copy() for cat, phrases in phrases_by_category.items()}

    print(f"Sending response #{sent_count + 1} ...")
    payload, phrase, updated_categorized, updated_dots = generate_one_response(
        sent_count, categorized, original, dots_left
    )

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://docs.google.com/forms/d/e/1FAIpQLSehIJDYbGUUvTEWOiq6WQQ_eV250l7B4-f8VHz8AGdzxucFoQ/viewform',
        'Origin': 'https://docs.google.com',
    }

    try:
        response = requests.post(URL, data=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Response #{sent_count + 1} sent. Phrase: \"{phrase}\"")
            state['sent_count'] = sent_count + 1
            state['categorized'] = updated_categorized
            state['dots_left'] = updated_dots
            save_state(state)
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"🔴 Exception: {e}")

if __name__ == "__main__":
    main()
