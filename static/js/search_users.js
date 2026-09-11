document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('user-search');
    const resultsContainer = document.getElementById('search-results');

    searchInput.addEventListener('input', function () {
        const searchQuery = searchInput.value.trim();

        if (searchQuery === '') {
            resultsContainer.innerHTML =
                '<p>Enter a search term to find users.</p>';
            return;
        }

        fetch(`/api/users/?q=${encodeURIComponent(searchQuery)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to search users.');
                }

                return response.json();
            })
            .then(users => {
                displaySearchResults(users);
            })
            .catch(error => {
                console.error(error);
                resultsContainer.innerHTML =
                    '<p>Unable to load search results.</p>';
            });
    });

    function displaySearchResults(users) {
        resultsContainer.innerHTML = '';

        if (users.length === 0) {
            const message = document.createElement('p');
            message.textContent = 'No users found.';
            resultsContainer.appendChild(message);
            return;
        }

        users.forEach(function (user) {
            const userElement = document.createElement('div');

            const name = document.createElement('h3');
            name.textContent = user.full_name;

            const username = document.createElement('p');
            username.textContent = `Username: ${user.username}`;

            const role = document.createElement('p');
            role.textContent = `Role: ${user.role}`;

            const email = document.createElement('p');
            email.textContent = `Email: ${user.email}`;

            const profileLink = document.createElement('a');
            profileLink.href =
                `/accounts/users/${encodeURIComponent(user.username)}/`;
            profileLink.textContent = 'View Profile';

            userElement.appendChild(name);
            userElement.appendChild(username);
            userElement.appendChild(role);
            userElement.appendChild(email);
            userElement.appendChild(profileLink);

            resultsContainer.appendChild(userElement);
        });
    }
});