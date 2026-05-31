import ollama
import json
from pathlib import Path

from config import RESULTS_DIR
from config import OLLAMA_MODEL

class OllamaService:
    
    
    @staticmethod
    def _call_ollama(prompt: str, temperature: float = 0.3) -> str:
        
        response = ollama.chat(
            model = OLLAMA_MODEL,
            messages = [{"role": "user", "content": prompt}],
            options = {"temperature": temperature}
        )

        return response['message']['content'].strip()


    @staticmethod
    async def label_speakers(transcript: dict) -> list:
        
        segments_text = "\n".join(
            f"{segment['start']}-{segment['end']}: {segment['text']}" 
            for segment in transcript["segments"][:50]
        )

        prompt = f"""Ты — эксперт по анализу деловых совещаний на русском языке.

        У тебя есть фрагмент транскрипции совещания (первые 50 сегментов). 
        В транскрипции спикеры обозначены как Speaker 1, Speaker 2 и т.д.

        Твоя задача: определить реальные имена и роли участников **только на основе содержания речи**, обращений друг к другу и контекста. 
        Не придумывай имена, если их нет в тексте.

        Вот фрагмент транскрипции:
        {segments_text}

        Верни **строго только валидный JSON** — массив объектов. Никакого дополнительного текста до или после JSON.

        Пример правильного ответа:
        [
            {{"speaker_id": "Speaker 1", "name": "Иванов Иван Иванович", "role": "Руководитель отдела продаж"}},
            {{"speaker_id": "Speaker 2", "name": "Петрова Анна Сергеевна", "role": "Менеджер по маркетингу"}},
            {{"speaker_id": "Speaker 3", "name": "None", "role": "None"}}
        ]

        Правила:
        - Если имя или роль точно не определяются — пиши "None"
        - speaker_id должен совпадать с оригинальным (Speaker 1, Speaker 2 и т.д.)
        - Будь максимально точным и консервативным.

        JSON:"""

        result = OllamaService._call_ollama(prompt, temperature = 0.1)

        try:
            return json.loads(result)
        except:
            return [{"speaker_id": speaker["speaker_id"], "name": speaker["speaker_id"], "role": "Участник"} 
                    for speaker in [{"speaker_id": f"Speaker {i + 1}"} for i in range(5)]]


    @staticmethod
    async def extract_tasks(full_text: str, speakers: list) -> list:
        
        speaker_list = "\n".join(f"- {speaker['speaker_id']}: {speaker['name']} ({speaker.get('role','')})" for speaker in speakers)

        prompt = f"""Ты — эксперт по извлечению задач из протоколов совещаний на русском языке.

        Участники совещания:
        {speaker_list}

        Полный текст совещания:
        {full_text[:12000]}

        Извлеки **все** поставленные задачи, поручения и action items.

        Верни **строго только валидный JSON** — массив объектов. Ничего больше.

        Формат каждого объекта:
        {{
            "description": "Подробное описание задачи",
            "assignee": "ФИО ответственного или \"Команда\", если неясно",
            "deadline": "15.04.2026 или null, если срок не указан",
            "status": "Новая"
        }}

        Пример:
        [
            {{"description": "Подготовить отчёт по продажам за март", "assignee": "Иванов Иван Иванович", "deadline": "15.04.2026", "status": "Новая"}},
            {{"description": "Организовать встречу с клиентом X", "assignee": "Команда", "deadline": null, "status": "Новая"}}
        ]

        Правила:
        - Если ответственный не указан явно — используй "Команда"
        - Если срок не упомянут — deadline = null
        - Описывай задачу полно и понятно

        JSON:"""

        result = OllamaService._call_ollama(prompt, temperature = 0.1)

        try:
            return json.loads(result)
        except:
            return []


    @staticmethod
    async def generate_protocol(full_text: str, speakers: list, tasks: list) -> str:
        
        speaker_info = "\n".join(f"**{speaker['speaker_id']}** — {speaker['name']} ({speaker.get('role','Участник')})" for speaker in speakers)
        tasks_md = "\n".join(f"- **{task['assignee']}**: {task['description']} (срок: {task.get('deadline','—')})" for task in tasks)

        prompt = f"""Ты — профессиональный делопроизводитель, специалист по составлению протоколов совещаний на русском языке.

        Сформируй **формальный и структурированный протокол** совещания в формате Markdown.

        Участники:
        {speaker_info}

        Извлечённые задачи:
        {tasks_md}

        Полный текст транскрипции (для контекста):
        {full_text[:15000]}

        Используй следующую структуру (обязательно):

        # Протокол совещания от [дата, если известна, иначе «[Дата не указана]»]

        ## Участники
        {speaker_info}

        ## Повестка дня / Ключевые обсуждения
        Кратко суммируй основные темы и ход обсуждения (3–7 пунктов).

        ## Принятые решения и задачи
        Перечисли все решения и задачи. Используй извлечённые задачи выше.

        ## Следующие шаги
        Кратко о том, что планируется дальше.

        Сделай текст формальным, лаконичным, объективным и удобным для чтения. 
        Используй деловой стиль русского языка.
        Не добавляй информацию, которой нет в транскрипции и задачах.

        Протокол:"""

        return OllamaService._call_ollama(prompt, temperature = 0.3)