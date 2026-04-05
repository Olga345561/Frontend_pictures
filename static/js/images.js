document.addEventListener('DOMContentLoaded', () => {
    // Реєструємо гарячі клавіші для повернення
    if (typeof registerKeyboardShortcuts === 'function') {
        registerKeyboardShortcuts('/');
    }

    // Кліки по вкладках
    document.getElementById('upload-tab-btn')?.addEventListener('click', () => {
        window.location.href = '/upload.html';
    });

    document.getElementById('images-tab-btn')?.addEventListener('click', () => {
        window.location.href = '/images.html';
    });

    if (typeof updateTabStyles === 'function') {
        updateTabStyles();
    }

    const container = document.getElementById('gallery-container');
    const paginationContainer = document.getElementById('gallery-pagination');
    let currentPage = 1;

    // 1. Отримання даних
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
                container.innerHTML = '<p class="db-gallery__empty">Помилка завантаження даних</p>';
            }
        }
    };

    // 2. Малювання таблиці (З ПРЕВ'Ю)
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
        const headers = ['Зображення', 'Назва', 'Оригінал', 'Розмір (КБ)', 'Дата', 'Тип', 'Дія'];

        headers.forEach(text => {
            const th = document.createElement('th');
            th.textContent = text;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        items.forEach(item => {
            const tr = document.createElement('tr');

            // Комірка Прев'ю
            const tdPreview = document.createElement('td');
            tdPreview.className = 'db-gallery__td-preview';
            const imgPreview = document.createElement('img');
            imgPreview.src = '/images/' + item.filename;
            imgPreview.alt = item.original_name;
            imgPreview.className = 'db-gallery__preview-icon';
            tdPreview.appendChild(imgPreview);
            tr.appendChild(tdPreview);

            // Комірка Назва (посилання)
            const tdLink = document.createElement('td');
            const a = document.createElement('a');
            a.href = '/images/' + item.filename;
            a.target = '_blank';
            a.textContent = item.filename;
            tdLink.appendChild(a);
            tr.appendChild(tdLink);

            // Оригінальна назва
            const tdOriginal = document.createElement('td');
            tdOriginal.textContent = item.original_name;
            tr.appendChild(tdOriginal);

            // Розмір
            const tdSize = document.createElement('td');
            tdSize.textContent = (item.size / 1024).toFixed(1);
            tr.appendChild(tdSize);

            // Дата
            const tdDate = document.createElement('td');
            tdDate.textContent = item.upload_time;
            tr.appendChild(tdDate);

            // Тип
            const tdType = document.createElement('td');
            tdType.textContent = item.file_type;
            tr.appendChild(tdType);

            // Дія (Видалити)
            const tdAction = document.createElement('td');
            const btn = document.createElement('button');
            btn.className = 'db-gallery__delete-btn';
            btn.textContent = 'Видалити';

            btn.onclick = async () => {
                if (confirm(`Видалити зображення ${item.original_name}?`)) {
                    try {
                        const response = await fetch('/delete/' + item.id, { method: 'POST' });

                        if (response.ok) {
                            // --- ПРАЦЮЄМО З LOCALSTORAGE ---
                            const deleteData = {
                                fileName: item.original_name,
                                dbId: item.id,
                                date: new Date().toLocaleString()
                            };

                            // Зберігаємо об'єкт у вигляді рядка
                            localStorage.setItem('lastDeleted', JSON.stringify(deleteData));

                            // Викликаємо функцію для відображення напису (додамо її нижче)
                            showDeleteLog();
                            fetchAndRender(currentPage);
                        } else {
                            alert('Не вдалося видалити файл на сервері. Спробуйте пізніше.');
                        }
                    } catch (error) {
                        console.error('Помилка видалення:', error);
                        alert('Помилка мережі. Перевірте з’єднання.');
                    }
                }
            };

            tdAction.appendChild(btn);
            tr.appendChild(tdAction);

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        container.appendChild(table);
    };

    // 3. ФУНКЦІЯ ПАГІНАЦІЇ
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

    const showDeleteLog = () => {
        const rawData = localStorage.getItem('lastDeleted');
        if (!rawData) return;

        const data = JSON.parse(rawData);
        let logBlock = document.getElementById('delete-info-display');

        if (!logBlock) {
            logBlock = document.createElement('div');
            logBlock.id = 'delete-info-display';
            // Стиль, щоб це виглядало як лог
            logBlock.style.cssText = 'margin-top: 20px; padding: 10px; background: #eee; border-radius: 5px; color: #333;';
            container.parentElement.appendChild(logBlock);
        }

        logBlock.innerHTML = `<strong>Останнє видалення:</strong> ${data.fileName} (ID: ${data.dbId}) о ${data.date}`;
    };

    // Обов'язково викликаємо її тут, щоб при оновленні сторінки напис залишався
    showDeleteLog();
});