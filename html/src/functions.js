const expandableButtons = document.querySelectorAll('.menu-box-title');
expandableButtons.forEach(button => {
    const courses = button.parentNode.querySelectorAll('.sub-menu-box')
    button.addEventListener("click", () => {
        courses.forEach(course => {
            course.style.display = course.style.display === 'none' ? 'block' : 'none';

        })
    })
})

const checkIcons = document.querySelectorAll('.simple-line-icons--check, .lets-icons--check-fill');
checkIcons.forEach(icon => {
    const box = icon.closest('.sub-menu-box');
    icon.addEventListener('click', () => {
        icon.classList.toggle('simple-line-icons--check');
        icon.classList.toggle('lets-icons--check-fill');
        box.classList.toggle('is-secondary-color');
        box.classList.toggle('is-fifth-color');
    })
})