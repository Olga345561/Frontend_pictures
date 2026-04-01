document.addEventListener('DOMContentLoaded', () => {
    // Реєструємо гарячі клавіші (Escape/F5) для повернення на головну
    if (typeof registerKeyboardShortcuts === 'function') {
        registerKeyboardShortcuts('/');
    }

    // Обробка кліку на вкладку Upload
    document.getElementById('upload-tab-btn')?.addEventListener('click', () => {
    window.location.href = '/upload.html';    //Повернення на вкладку Upload
    });

    // Обробка кліку на вкладку Images
    document.getElementById('images-tab-btn')?.addEventListener('click', () => {
        window.location.href = '/images.html';
    });

    // Оновлюємо підсвітку вкладок (якщо функція є в common.js)
    if (typeof updateTabStyles === 'function') {
        updateTabStyles();
    }

    const container = document.getElementById('gallery-container');
    const paginationContainer = document.getElementById('gallery-pagination');
    let currentPage = 1;

    // Функція отримання даних з сервера
    const fetchAndRender = async (page) => {
        try {
            const response = await fetch('/api/images?page=' + page);
            if (!response.ok) throw new Error('Помилка сервера');

            const data = await response.json();
            currentPage = data.page;
            renderTable(data.items);
            renderPagination(data.page, data.total_pages);
        } catch (error) {
            console.error(error);
            if (container) {
                container.innerHTML = '<p class="db-gallery__empty">Помилка завантаження даних з бази</p>';
            }
        }
    };

    // Функція малювання таблиці
    const renderTable = (items) => {
        if (!container) return;
        container.textContent = '';

        if (!items || items.length === 0) {
            container.innerHTML = '<p class="db-gallery__empty">Немає завантажених зображень</p>';
            return;
        }

        const table = document.createElement('table');
        table.className = 'db-gallery__table';

        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        ['Назва', 'Оригінал', 'Розмір (КБ)', 'Дата', 'Тип', 'Дія'].forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        items.forEach(item => {
            const tr = document.createElement('tr');

            // Назва файлу (посилання)
            const tdLink = document.createElement('td');
            const a = document.createElement('a');
            a.href = '/images/' + item.filename;
            a.target = '_blank';
            a.textContent = item.filename;
            tdLink.appendChild(a);

            // Інші колонки
            const tdOriginal = document.createElement('td');
            tdOriginal.textContent = item.original_name;

            const tdSize = document.createElement('td');
            tdSize.textContent = (item.size / 1024).toFixed(1);

            const tdDate = document.createElement('td');
            tdDate.textContent = item.upload_time;

            const tdType = document.createElement('td');
            tdType.textContent = item.file_type;

            // Кнопка видалення
            const tdAction = document.createElement('td');
            const btn = document.createElement('button');
            btn.className = 'db-gallery__delete-btn';
            btn.textContent = 'Видалити';
            btn.onclick = async () => {
                if (confirm('Видалити це зображення?')) {
                    await fetch('/delete/' + item.id, { method: 'POST' });
                    fetchAndRender(currentPage);
                }
            };
            tdAction.appendChild(btn);

            tr.append(tdLink, tdOriginal, tdSize, tdDate, tdType, tdAction);
            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        container.appendChild(table);
    };

    // Пагінація (залишаємо як було, вона створює елементи динамічно)
    const renderPagination = (page, totalPages) => {
        if (!paginationContainer) return;
        paginationContainer.textContent = '';
        if (totalPages <= 1) return;

        const nav = document.createElement('div');
        nav.className = 'db-gallery__pagination';

        const createBtn = (text, targetPage, active) => {
            const btn = document.createElement('button');
            btn.textContent = text;
            btn.className = 'db-gallery__page-btn';
            if (!active) btn.classList.add('db-gallery__page-btn--disabled');
            btn.onclick = () => { if (active) fetchAndRender(targetPage); };
            return btn;
        };

        nav.appendChild(createBtn('Назад', page - 1, page > 1));
        const info = document.createElement('span');
        info.textContent = ` Стор. ${page} з ${totalPages} `;
        nav.appendChild(info);
        nav.appendChild(createBtn('Далі', page + 1, page < totalPages));

        paginationContainer.appendChild(nav);
    };

    fetchAndRender(1);
});