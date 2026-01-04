document.addEventListener('DOMContentLoaded', function () {
    // 1. ЛОГІКА ВИПАДКОВОЇ КАРТИНКИ
    // Знаходимо всі блоки з картинками
    const allImgBloks = document.querySelectorAll('.pictures_img');

    // Перевіряємо, чи ми взагалі знайшли якісь картинки (щоб не було помилки)
    if (allImgBloks.length > 0) {
        // Генеруємо випадковий індекс: від 0 до (кількість картинок - 1)
        const randomIndex = Math.floor(Math.random() * allImgBloks.length);

        // Вибираємо випадковий блок
        const randomBlock = allImgBloks[randomIndex];

        // Робимо його видимим
        randomBlock.classList.add('is-visible');
    }

    // 2. КОЛІР ФОНУ
    // Встановлюємо колір фону для всієї сторінки
    document.body.style.setProperty('background-color', '#151515');

    // 3. ЛОГІКА КНОПКИ
    const showcaseButton = document.querySelector('.header_button_btn');

    if (showcaseButton) {
        showcaseButton.addEventListener('click', function () {
            // Перехід на сторінку завантаження
            window.location.href = '../file_html/upload.html';
        });
    }
});