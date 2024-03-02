const sendRequest = async (url, method = 'GET', body = null) => {
    try {
        const response = await fetch(`http://83.7.232.237:8080/api/${url}`, {
            method: method,
            headers: {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
                "Content-Type": "application/json",
                "Cookie": "session=eyJpZCI6eyIgdSI6IjBkMzc2NTA5ZmU3OTRmMGU5N2FkYjBjM2Q5Y2ZjNDg2In19.ZeDY9A.RM3Fbf7UwPpvSnMgW4Chv4O0kjw; HttpOnly; Path=/",
            },
            body: body ? JSON.stringify(body) : null,
            mode: 'cors'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }


        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error during the fetch operation: ", error.message);
        throw error;
    }
}