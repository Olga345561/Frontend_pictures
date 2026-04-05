document.addEventListener('DOMContentLoaded',function () {
    document.addEventListener('keydown', function (event) {
        if(event.key ==='Escape' || event.key === 'F5') {
            event.preventDefault();

            sessionStorage.removeItem('pageWasVisited');
            window.location.href = '../index.html';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const imagesButton = document.getElementById('images-tab-btn');
    const fileUpLoad = document.getElementById('file-upload');
    const dropzone = document.querySelector('.upload_dropzone');
    const currentUploadInput = document.querySelector('.upload_input');
    const copyButton = document.querySelector('.upload_copy_btn');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

        const isImagesPage = window.location.pathname.includes('images.html');

        uploadTab.classList.remove('upload_tab--active');
        imagesTab.classList.remove('upload_tab--active');

        if(isImagesPage) {
            imagesTab.classList.add('upload_tab--active');
        } else {
            uploadTab.classList.add('upload_tab--active');
        }
    };

    const handleAndStoreFiles = async (files) => {
        if (!files || files.length === 0) return;

        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const MAX_SIZE_BYTES = 5 * 1024 * 1024;

        for (const file of files) {
            // 1. Перевірка файлу
            if (!allowedTypes.includes(file.type) || file.size > MAX_SIZE_BYTES) {
                alert(`Файл ${file.name} занадто великий або не того формату!`);
                continue;
            }

            // 2. Створюємо "коробку" для відправки файлу (FormData)
            const formData = new FormData();
            formData.append('file', file); // Ключ 'file' має збігатися з тим, що чекає Python

            try {
                // 3. ВІДПРАВКА НА СЕРВЕР
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    console.log('Файл успішно збережено на сервері:', result);
                    if (currentUploadInput) {
                        currentUploadInput.value = `http://localhost:8080/images/${result.filename}`;
                    }
                    alert(`Файл ${file.name} успішно завантажено!`);
                } else {
                    alert('Помилка сервера: ' + result.error);
                }

            } catch (error) {
                console.error('Помилка мережі:', error);
                alert('Не вдалося зв’язатися з сервером. Перевірте, чи запущений app.py');
            }
        }
    };

    if (copyButton && currentUploadInput) {
    copyButton.addEventListener('click', () => {
        const textToCopy = currentUploadInput.value;

        // 1. Якщо посилання порожнє (наприклад, ще не завантажили файл) — нічого не робимо
        if (!textToCopy || textToCopy.includes('https://sharefile.xyz/undefined')) {
            alert("Спочатку завантажте файл!");
            return;
        }

        // 2. Спроба скопіювати через сучасний API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy)
                .then(() => showSuccess())
                .catch(err => console.error('Clipboard error:', err));
        } else {
            // 3. РЕЗЕРВНИЙ МЕТОД (працює на 192.168... та HTTP)
            const textArea = document.createElement("textarea");
            textArea.value = textToCopy;

            // Робимо поле невидимим
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            textArea.style.top = "0";
            document.body.appendChild(textArea);

            textArea.focus();
            textArea.select();

            try {
                const successful = document.execCommand('copy');
                if (successful) showSuccess();
            } catch (err) {
                console.error('Fallback copy failed', err);
            }

            document.body.removeChild(textArea);
        }
    });

    // Окрема функція для візуального ефекту, щоб не дублювати код
    function showSuccess() {
        copyButton.textContent = 'COPIED!';
        copyButton.classList.add('upload_copy_btn--success'); // Можна додати колір у CSS
        setTimeout(() => {
            copyButton.textContent = 'COPY';
            copyButton.classList.remove('upload_copy_btn--success');
        }, 2000);
    }
}

    if (imagesButton) {
        imagesButton.addEventListener('click', () => {
            window.location.href = 'images.html';
        });
    }
    fileUpLoad.addEventListener('change', (event) => {
        handleAndStoreFiles(event.target.files);
        event.target.value = '';
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    dropzone.addEventListener('drop', (event) => {
        handleAndStoreFiles(event.dataTransfer.files);
    });

    updateTabStyles();
});













