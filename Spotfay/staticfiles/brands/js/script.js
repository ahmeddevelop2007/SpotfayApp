function toggleEdit(infoId, editId, button) {
    const infoDiv = document.getElementById(infoId);
    const editDiv = document.getElementById(editId);
    const buttons = document.querySelectorAll('.edit-btn')
    
    // Toggle visibility
    if (infoDiv.classList.contains('d-none')) { // not visible
        infoDiv.classList.remove('d-none');
        infoDiv.classList.add('d-block');
        editDiv.classList.remove('d-block');
        editDiv.classList.add('d-none');
        // enable buttons
        buttons.forEach(button => button.style.display = 'block');
    } else {
        infoDiv.classList.remove('d-block');
        infoDiv.classList.add('d-none');
        editDiv.classList.remove('d-none');
        editDiv.classList.add('d-block');
        // Disable buttons
        buttons.forEach(button => button.style.display = 'none');        
    }
}
const scrollBtn = document.getElementById('scroll-btn');
const scrollDiv = document.getElementById('scroll-div');

scrollBtn.addEventListener('click', () => {
    let scrollPosition = scrollDiv.scrollLeft;
    const scrollAmount = 70; // adjust this value to change the scroll amount
    scrollPosition += scrollAmount;
    scrollDiv.scrollTo({ left: scrollPosition, behavior: 'smooth' });
});

