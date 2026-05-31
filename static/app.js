let uploadedFilename = null;
let transcriptFilename = null;
let currentResult = null;
let history = JSON.parse(localStorage.getItem('meetingHistory') || '[]');

const API_BASE = '/api';

async function uploadRecord() {
    
    const fileInput = document.getElementById('recordFile');
    
    if (!fileInput.files[0]) return alert('Выберите файл');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const status = document.getElementById('uploadStatus');
    status.textContent = 'Загрузка файла...';

    try {
        
        const response = await fetch(`${API_BASE}/upload-record`, { method: 'POST', body: formData });
        const data = await response.json();

        if (response.ok) {
            uploadedFilename = data.filename;
            status.innerHTML = `Загружен: <strong>${data.filename}</strong>`;
            document.getElementById('transcribeBtn').disabled = false;
        } else {
            status.textContent = `Ошибка: ${data.detail || 'Неизвестная ошибка'}`;
        }

    } catch (e) {
        status.textContent = 'Ошибка соединения';
    }

}

async function startTranscription() {

    if (!uploadedFilename) return;

    const btn = document.getElementById('transcribeBtn');
    const status = document.getElementById('transcribeStatus');
    const thinking = document.getElementById('transcribeThinking');

    btn.disabled = true;
    thinking.classList.remove('hidden');
    status.textContent = '';

    try {

        const response = await fetch(`${API_BASE}/transcribe?filename=${encodeURIComponent(uploadedFilename)}`, {
            method: 'POST'
        });

        const data = await response.json();

        thinking.classList.add('hidden');

        if (response.ok) {
            transcriptFilename = data.transcript_file.split('/').pop();
            status.innerHTML = `Транскрипция завершена (${data.segments_count} сегментов)`;
            document.getElementById('transcriptPreview').classList.remove('hidden');
            document.getElementById('transcriptPreview').innerHTML = `<strong>Превью:</strong><br>${data.full_text_preview}`;
            document.getElementById('processBtn').disabled = false;
        } else {
            status.textContent = `Ошибка: ${data.detail}`;
        }

    } catch (e) {
        thinking.classList.add('hidden');
        status.textContent = 'Ошибка при транскрипции';
    }

}

async function processMeeting() {
    
    if (!transcriptFilename) return;

    const btn = document.getElementById('processBtn');
    const status = document.getElementById('processStatus');
    const thinking = document.getElementById('processThinking');

    btn.disabled = true;
    thinking.classList.remove('hidden');
    status.textContent = '';

    try {
        
        const response = await fetch(`${API_BASE}/process-meeting?transcript_filename=${encodeURIComponent(transcriptFilename)}`, {
            method: 'POST'
        });
        
        const data = await response.json();

        thinking.classList.add('hidden');

        if (response.ok) {
            currentResult = data;
            status.innerHTML = `Обработка завершена!`;
            document.getElementById('results').classList.remove('hidden');
            
            renderResults();
            saveToHistory(data);
        } else {
            status.textContent = `Ошибка: ${data.detail}`;
        }

    } catch (e) {
        thinking.classList.add('hidden');
        status.textContent = 'Ошибка соединения с сервером';
    }

}

function saveToHistory(result) {
    
    const entry = {
        id: Date.now(),
        filename: result.filename || "Совещание",
        date: new Date().toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
        speakersCount: result.speakers ? result.speakers.length : 0,
        tasksCount: result.tasks ? result.tasks.length : 0,
        result: result
    };

    history.unshift(entry);
    
    if (history.length > 15) history.pop();
    
    localStorage.setItem('meetingHistory', JSON.stringify(history));

}

function showHistory() {
    
    let html = `<h3 class="font-semibold text-xl mb-6 flex items-center gap-3"><i class="fa-solid fa-history"></i> История совещаний</h3>`;

    if (history.length === 0) {
        html += `<p class="text-slate-500 text-center py-8">Пока нет обработанных совещаний.<br>Обработайте первое!</p>`;
    } else {
        html += `<div class="space-y-3 max-h-[420px] overflow-y-auto pr-2">`;
        history.forEach(item => {
            html += `
                <div onclick="loadHistoryItem(${item.id})" 
                     class="history-item p-5 bg-white border border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 transition-all">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-medium text-slate-900">${item.filename}</div>
                            <div class="text-xs text-slate-400 mt-1">${item.date}</div>
                        </div>
                        <div class="text-right text-xs">
                            <div>${item.speakersCount} участников</div>
                            <div class="text-emerald-600">${item.tasksCount} задач</div>
                        </div>
                    </div>
                </div>`;
        });
        html += `</div>`;
    }

    const modal = document.createElement('div');
    
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content p-8">
            ${html}
            <button onclick="this.closest('.modal').remove()" 
                    class="mt-8 w-full py-4 bg-slate-100 hover:bg-slate-200 rounded-2xl font-medium">
                Закрыть
            </button>
        </div>`;
    
    document.body.appendChild(modal);

}

function loadHistoryItem(id) {

    const item = history.find(h => h.id === id);
    
    if (!item || !item.result) return;

    currentResult = item.result;
    document.getElementById('results').classList.remove('hidden');
    
    renderResults();
    
    document.querySelector('.modal').remove();

}

function renderResults() {
    
    if (!currentResult) return;

    let html = '<tr><th>ID</th><th>Имя</th><th>Роль</th></tr>';
    
    currentResult.speakers.forEach(s => {
        html += `<tr><td>${s.speaker_id}</td><td>${s.name}</td><td>${s.role || '—'}</td></tr>`;
    });

    document.getElementById('speakersTable').innerHTML = html;

    html = '<tr><th>Задача</th><th>Ответственный</th><th>Срок</th><th>Статус</th></tr>';
    
    currentResult.tasks.forEach(t => {
        html += `<tr><td>${t.description}</td><td>${t.assignee}</td><td>${t.deadline || '—'}</td><td>${t.status}</td></tr>`;
    });
    
    document.getElementById('tasksTable').innerHTML = html;

    document.getElementById('protocolContent').innerHTML = 
        currentResult.protocol_markdown
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    document.getElementById('fullTranscript').textContent = currentResult.full_text || '';

}

function showTab(n) {

    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab${n}`).classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach((el, i) => el.classList.toggle('active', i === n));

}

function downloadProtocol() {
    
    if (!currentResult) return;
    
    const blob = new Blob([currentResult.protocol_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `протокол_${(currentResult.filename || 'совещание').replace('.json','')}.md`;
    a.click();
    
    URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', () => {
    showTab(0);
});