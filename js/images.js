document.addEventListener('DOMContentLoaded',function () {
    document.addEventListener('keydown', function (event) {
        if(event.key ==='Escape' || event.key === 'F5') {
            event.preventDefault();
            window.location.href = 'upload.html';
        }
    });

    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

        const isImagesPage = window.location.pathname.includes('images.html');

        uploadTab.classList.remove('upload_tab--active');
        imagesTab.classList.remove('upload_tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload_tab--active')
        } else {
             uploadTab.classList.add('upload_tab--active')
        }
    };

    const displayFiles = () => {
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
        fileListWrapper.innerHTML = '';

        if (storedFiles.length === 0) {
            fileListWrapper.innerHTML = '<p class="upload_promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
        } else {
            // 1. Створюємо контейнер для шапки таблиці
            const container = document.createElement('div');
            container.className = 'file-list-container';
            // 2. Наповнюємо шапку назвами колонок
            const header = document.createElement('div');
            header.className = 'file-list-header'
            header.innerHTML = `
                <div class="file-col file-col-name">Name</div>
                <div class="file-col file-col-url">URL</div>
                <div class="file-col file-col-delete">Delete</div>
            `;
            container.appendChild(header);

            const list = document.createElement('div');
            list.id = 'file-list';

            storedFiles.forEach((fileData, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-list-item';
                fileItem.innerHTML = `
                <div class="file-col file-col-name">
                    <span class="file-icon"><img src="../img/photo.png" alt="file img"></span>
                    <span class="file-name">${fileData.name}</span>
                </div>
                <div class="file-col file-col-url">https://sharefile.xyz/${fileData.name}</div>
                <div class="file-col file-delete">
                    <button class="delete-btn" data-index="${index}"><img src="../img/delete.png" alt="delete img"></button>
                </div>
            `;
            list.appendChild(fileItem);
            });

            container.appendChild(list);
            fileListWrapper.appendChild(container);
            addDeleteListeners();
        }
        updateTabStyles();
    };

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach(button => {
           button.addEventListener('click', (event) => {
              const indexToDelete = parseInt(event.currentTarget.dataset.index);
              let storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
              storedFiles.splice(indexToDelete,1);
              localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
              displayFiles();
           });
        });
    };

    if(uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = 'upload.html';
        });
    }
    displayFiles();

});






















