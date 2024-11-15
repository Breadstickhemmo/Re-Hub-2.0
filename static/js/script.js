// Показать форму регистрации
function showRegister() {
    document.getElementById('registration').style.display = 'block';
    document.getElementById('registration-overlay').style.display = 'block';
}

// Скрыть форму регистрации
function hideRegistration() {
    document.getElementById('registration').style.display = 'none';
    document.getElementById('registration-overlay').style.display = 'none';
}

// Добавляем обработчик для кнопки регистрации
document.getElementById('registrationForm').addEventListener('submit', function(event) {
    hideRegistration();
});

// Показать форму логина
function showLogin() {
    document.getElementById('login').style.display = 'block';
    document.getElementById('login-overlay').style.display = 'block';
}

// Скрыть форму логина
function hideLogin() {
    document.getElementById('login').style.display = 'none';
    document.getElementById('login-overlay').style.display = 'none';
}

// Добавляем обработчик для кнопки логина
document.getElementById('loginForm').addEventListener('submit', function(event) {
    hideLogin();
});

document.addEventListener('DOMContentLoaded', function() {
    // Найти все flash-сообщения
    document.querySelectorAll('.flash-message').forEach(function(message) {
        // Тайм-аут для начала исчезновения через 1 секунду
        setTimeout(function() {
            message.classList.add('fade-out');
        }, 1000); // Начало исчезновения через 1 секунду
        
        // Удаление элемента после завершения анимации (еще 1 секунда для анимации)
        setTimeout(function() {
            message.remove();
        }, 2000); // Общее время: 1 секунда задержки + 1 секунда на анимацию
    });
});

function togglePasswordChange() {
    const passwordChangeSection = document.getElementById('changePasswordSection');
    if (passwordChangeSection.style.display === 'none' || passwordChangeSection.style.display === '') {
      passwordChangeSection.style.display = 'block';
    } else {
      passwordChangeSection.style.display = 'none';
    }
  }

function toggleEmailConfirmation() {
    const emailConfirmationSection = document.getElementById('emailConfirmationSection');
    if (emailConfirmationSection.style.display === 'none' || emailConfirmationSection.style.display === '' ) {
        emailConfirmationSection.style.display = 'block';
    } else {
        emailConfirmationSection.style.display = 'none';
    } 
}

// Функция для начала оценки
function startKosmo() {
    alert("Запуск оценки совместимости. Ожидайте дальнейшей разработки.");
}