
export default async function apiFetch(endpoint: string, method: string = 'GET', fetchData?: any) {
    //base api
    const apiBase = import.meta.env.VITE_API_URL;

    let token = localStorage.getItem('accessToken'); // get token from local storage
    const headers: Record<string, string> = { // construct the request headers
        'Content-Type': 'application/json'
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`; // add token to headers authorization
    }

    const options: RequestInit = { // construct an options for the fetch second argument, RequestInit is a build in type for the request contents
        method: method.toUpperCase(),
        headers: headers,
    };

    if (fetchData && options.method !== 'GET') {
        options.body = JSON.stringify(fetchData); // add data if the method is not get
    }

    try {
        // first try on the endpoint call 
        let response = await fetch(`${apiBase}/${endpoint}/`, options);
        
        // if access tokens expires try to refresh the token
        if (response.status === 401) {
            const refreshToken = localStorage.getItem('refreshToken');

            if (refreshToken) {
                
                // call the refresh token api
                const refreshResponse = await fetch(`${apiBase}/api/token/refresh/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ refresh: refreshToken}),
                });

                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();

                    // save the new tokens on storage adn safeguard in case token rotation is disabled
                    localStorage.setItem('accessToken', data.access);

                    if (data.refresh) {
                        localStorage.setItem('refreshToken', data.refresh);
                    }

                    // update headers with new token and retry the original fetch
                    headers['Authorization'] = `Bearer ${data.access}`;
                    options.headers = headers;

                    response = await fetch(`${apiBase}/${endpoint}/`, options);

                    // if 30 minutes token is invalid close user session
                } else {
                    localStorage.clear()
                    window.location.href = '/login';
                }
                
            // return user to login in case that refresh token is not found
            } else {
                localStorage.clear()
                window.location.href = '/login';
            }

        }

        return response;

    } catch (err) {
        console.error(`API fetch error: ${err}`)
        throw err;

    }
}