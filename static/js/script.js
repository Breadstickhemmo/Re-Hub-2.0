// Показать форму регистрации
function showRegister() {
    document.getElementById('registration-overlay').style.display = 'flex'; // Показываем затемнение
    document.getElementById('registration').style.display = 'block'; // Показываем форму
}

// Скрыть форму регистрации
function hideRegistration() {
    document.getElementById('registration-overlay').style.display = 'none'; // Скрываем затемнение
    document.getElementById('registration').style.display = 'none'; // Скрываем форму
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

function toggleProfileEdit() {
    const profileEditSection = document.getElementById('profileEditSection');
    if (profileEditSection.style.display === 'none' || profileEditSection.style.display === '') {
        profileEditSection.style.display = 'block';
    } else {
        profileEditSection.style.display = 'none';
    }
}

function toggleProfessionalEdit() {
    const section = document.getElementById("professionalEditSection");
    if (section.style.display === 'none' || section.style.display === '') {
        section.style.display = 'block';
    } else {
        section.style.display = 'none';
    }
}

function toggleEmployerEdit() {
    const employerEditSection = document.getElementById('employerEditSection');
    if (employerEditSection.style.display === 'none' || employerEditSection.style.display === '') {
        employerEditSection.style.display = 'block';
    } else {
        employerEditSection.style.display = 'none';
    }
}

function toggleBusinessEdit() {
    const additionalOptions = document.getElementById('additionalBusinessOptions');
    if (additionalOptions.style.display === 'none' || additionalOptions.style.display === '') {
        additionalOptions.style.display = 'block'; // Показываем дополнительные опции
    } else {
        additionalOptions.style.display = 'none'; // Скрываем дополнительные опции
    }
}

function toggleEmployeesSection() {
    const employeesEditSection = document.getElementById('employeesEditSection');
    if (employeesEditSection.style.display === 'none' || employeesEditSection.style.display === '') {
        employeesEditSection.style.display = 'block';
    } else {
        employeesEditSection.style.display = 'none';
    }
}