document.addEventListener('DOMContentLoaded', () => {
    const albumCover = document.getElementById('album-cover');
    const optionsContainer = document.getElementById('options-container');
    const statusMessage = document.getElementById('status-message');
    const gameContainer = document.getElementById('game-container');

    async function loadPuzzle() {
    
        const response = await fetch('/api/get-album-puzzle');
        const data = await response.json();

        albumCover.src = `/static/images/${data.image}`;
        
        optionsContainer.innerHTML = ''; 

        data.options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.textContent = option;
            button.addEventListener('click', () => handleGuess(button));
            optionsContainer.appendChild(button);
        });
    }

    async function handleGuess(clickedButton) {
        const guess = clickedButton.textContent;
        const allButtons = optionsContainer.querySelectorAll('.option-btn');

        allButtons.forEach(btn => btn.disabled = true);

       
        const response = await fetch('/api/submit-guess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ guess: guess }),
        });
        const result = await response.json();

        if (result.success) {
            
            clickedButton.classList.add('correct');
            statusMessage.textContent = 'Correct! Redirecting...';
            
           
            document.body.classList.add('fade-out');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500); 

        } else {
            clickedButton.classList.add('wrong');
            statusMessage.textContent = 'Wrong answer. Try again.';
            gameContainer.classList.add('shake');

            setTimeout(() => {
                gameContainer.classList.remove('shake');
                statusMessage.textContent = '';
                allButtons.forEach(btn => {
                    btn.disabled = false;
                    btn.classList.remove('wrong');
                });
            }, 2000);
        }
    }

    loadPuzzle();
});