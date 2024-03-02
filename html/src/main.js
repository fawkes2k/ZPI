const init = (async () => {
    console.log('[LOG] main.js initialzied!');
    await sendRequest('login', 'POST', { email: "test@example.com", password: "alamatkota" })
        .then(data => console.log(data))
        .catch(error => console.error(error));

    await sendRequest('get_courses')
        .then(data => console.log(data))
        .catch(error => console.error(error));
})();